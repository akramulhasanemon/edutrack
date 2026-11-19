"""Academic coaching backed by Gemini, local Ollama LLMs, and an advanced offline expert inference engine."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from modules.grading import calculate_weighted_cgpa, grade_point_for_enrollment


def build_student_academic_profile(
    student_id: str,
    student_name: str,
    target_cgpa: float,
    program_credits: float,
) -> dict[str, Any]:
    """Load the student's latest academic, attendance, and schedule records."""
    from modules.crud import AcademicCRUD

    courses = AcademicCRUD.get_student_enrollments(student_id)
    attendance = AcademicCRUD.get_attendance(student_id)
    course_codes = {str(course["course_code"]) for course in courses}
    schedules = [
        routine
        for routine in AcademicCRUD.get_routines()
        if str(routine["course_code"]) in course_codes
    ]
    cgpa, graded_credits = calculate_weighted_cgpa(courses)
    weak_courses = [
        course
        for course in courses
        if (grade_point := grade_point_for_enrollment(course)) is not None
        and grade_point < 2.5
    ]
    return {
        "student_name": student_name,
        "student_id": student_id,
        "current_cgpa": cgpa,
        "graded_credits": graded_credits,
        "target_cgpa": target_cgpa,
        "program_credits": program_credits,
        "courses": courses,
        "weak_courses": weak_courses,
        "attendance": attendance,
        "schedules": schedules,
    }


class AIAdvisorEngine:
    """Generate personalized coaching, with Gemini cloud, local Ollama, and offline expert reasoning."""

    def __init__(self, api_key: str | None = None) -> None:
        self.client: Any | None = None
        self.cloud_error: str | None = (
            "Using personalized local coaching; no Gemini API key is configured."
            if not api_key or not api_key.strip()
            else None
        )
        if api_key and api_key.strip():
            try:
                from google import genai

                self.client = genai.Client(api_key=api_key.strip())
            except Exception as exc:
                self.cloud_error = f"Gemini could not be initialized ({type(exc).__name__})."

    def get_academic_advice(
        self,
        student_name: str,
        current_cgpa: float | None,
        completed_credits: float,
        weak_courses: Sequence[str] | Sequence[Mapping[str, Any]] | None,
        user_query: str,
        academic_profile: Mapping[str, Any] | None = None,
        conversation: Sequence[Mapping[str, str]] | None = None,
    ) -> str:
        """Answer a coaching question from academic history, recent chat, or offline expert reasoning."""
        profile = dict(academic_profile or {})
        profile.setdefault("student_name", student_name)
        profile.setdefault("current_cgpa", current_cgpa)
        profile.setdefault("graded_credits", completed_credits)
        profile.setdefault("weak_courses", list(weak_courses or []))

        # 1. Try Gemini Cloud if configured
        if self.client is not None:
            try:
                from google.genai import types

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_query,
                    config=types.GenerateContentConfig(
                        system_instruction=self._build_prompt(
                            profile, conversation
                        )
                    ),
                )
                answer = getattr(response, "text", None)
                if answer and answer.strip():
                    return answer.strip()
                self.cloud_error = "Gemini returned an empty response."
            except Exception as exc:
                self.cloud_error = (
                    f"Gemini request failed ({type(exc).__name__}); "
                    "using personalized local coaching."
                )

        # 2. Try Local Ollama LLM if available on localhost:11434 (100% offline)
        ollama_response = self._try_query_ollama(profile, user_query, conversation)
        if ollama_response:
            return ollama_response

        # 3. Fallback to Deep Academic Inference Engine (offline rule-based reasoning)
        return self._local_advice(profile, user_query)

    @classmethod
    def _try_query_ollama(
        cls,
        profile: Mapping[str, Any],
        query: str,
        conversation: Sequence[Mapping[str, str]] | None,
    ) -> str | None:
        """Query local Ollama server if running on localhost:11434 without internet."""
        import urllib.error
        import urllib.request

        try:
            prompt = cls._build_prompt(profile, conversation)
            payload = json.dumps({
                "model": "llama3.2:1b",
                "prompt": f"{prompt}\n\nStudent question: {query}",
                "stream": False,
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode())
                response_text = data.get("response", "").strip()
                if response_text:
                    return response_text
        except Exception:
            return None
        return None

    @staticmethod
    def _build_prompt(
        profile: Mapping[str, Any],
        conversation: Sequence[Mapping[str, str]] | None,
    ) -> str:
        system_instructions = (
            "You are EduTrack's strict but encouraging Academic Mentor and "
            "Trainer. Be direct, constructive, and specific; never shame the "
            "student or invent facts. Diagnose patterns using only the supplied "
            "records, state assumptions, and distinguish recommendations from "
            "known data. For study plans, give a realistic weekly schedule with "
            "priorities and measurable checkpoints. For exam strategy, give a "
            "course-aware revision sequence, active-recall practice, and an "
            "exam-day approach. For performance diagnostics, explain strengths, "
            "risks, and the highest-impact next actions. Address the student's "
            "latest question, keep the response readable, and ask one focused "
            "follow-up only when essential."
        )
        history = [
            {"role": item.get("role", ""), "text": item.get("text", "")}
            for item in (conversation or [])[-8:]
        ]
        context = json.dumps(
            {"academic_profile": profile, "recent_conversation": history},
            ensure_ascii=False,
            default=str,
            indent=2,
        )
        return (
            f"{system_instructions}\n\n"
            f"Complete student context from EduTrack SQLite:\n{context}\n\n"
            "Use the student's latest message as the question to answer."
        )

    @staticmethod
    def _local_advice(profile: Mapping[str, Any], question: str) -> str:
        """Deep Academic Inference Engine: Generates smart, mathematically rigorous offline coaching."""
        name = str(profile.get("student_name") or "Student")
        cgpa = profile.get("current_cgpa")
        credits = float(profile.get("graded_credits") or profile.get("completed_credits") or 0)
        target = profile.get("target_cgpa") or 3.85
        prog_credits = float(profile.get("program_credits") or 142.0)
        courses = list(profile.get("courses") or [])
        weak_courses = list(profile.get("weak_courses") or [])
        attendance = list(profile.get("attendance") or [])
        schedules = list(profile.get("schedules") or [])

        cgpa_display = f"{cgpa:.2f}" if isinstance(cgpa, (int, float)) else "N/A"
        rem_credits = max(prog_credits - credits, 0.0)

        # 1. Trajectory calculation
        req_gpa: float | None = None
        if isinstance(cgpa, (int, float)) and rem_credits > 0:
            total_credits = credits + rem_credits
            req_gpa = ((target * total_credits) - (cgpa * credits)) / rem_credits

        # 2. Extract weak courses and low attendance
        weak_names = [
            str(c.get("course_code") or c.get("course_title") or "Course")
            if isinstance(c, Mapping)
            else str(c)
            for c in weak_courses
        ]
        low_attendance = [
            item
            for item in attendance
            if isinstance(item.get("attendance_percentage"), (int, float))
            and item["attendance_percentage"] < 75
        ]

        q_lower = question.casefold()

        # --- 1. GREETINGS & CASUAL CONVERSATION (ENG / BANGLISH / BANGLA) ---
        if any(w in q_lower for w in (
            "how are you", "how r u", "kemon acho", "kemon aso", "ki obostha", "ki khobor",
            "valo aso", "bhalo aso", "valo acho", "bhalo acho", "kire", "bro", "dost",
            "কেমন আছো", "কেমন আছেন", "কি অবস্থা", "কী খবর"
        )):
            return (
                f"Hello {name}! 👋 আমি EduTrack AI, ভালো আছি এবং আপনার যেকোনো একাডেমিক সহায়তার জন্য প্রস্তুত (I am doing great and ready to assist you)!\n\n"
                f"📊 আপনার বর্তমান প্রোফাইল:\n"
                f"• Current CGPA: {cgpa_display} (Target: {target:.2f})\n"
                f"• Graded Credits: {credits:g} / {prog_credits:g} B.Sc. in CSE\n\n"
                "আজকে আপনি কী বিষয়ে জানতে চান? যেমন:\n"
                "1. 🎯 CGPA গোল অর্জনের স্ট্র্যাটেজি ('How to reach my target CGPA')\n"
                "2. 📅 ৭ দিনের পার্সোনালাইজড স্টাডি রুটিন ('7-Day Study Timetable')\n"
                "3. 🔄 কোন কোর্স রিটেক দিলে সর্বোচ্চ CGPA বাড়বে ('Retake Strategy')\n"
                "4. ⚡ পরীক্ষার আগের হাই-ইম্প্যাক্ট রিভিশন টেকনিক ('Exam Preparation')\n\n"
                "উপরে উল্লেখিত বিষয়গুলোতে প্রশ্ন করতে পারেন অথবা কুইক প্রম্পট বাটনে ক্লিক করতে পারেন!"
            )

        if any(q_lower.startswith(w) or q_lower == w for w in (
            "hi", "hello", "hey", "salam", "assalamu", "good morning", "good evening",
            "suprobhat", "হাই", "হ্যালো", "সালাম", "আসসালামু আলাইকুম"
        )):
            return (
                f"Hello {name}! 👋 Welcome to EduTrack AI.\n\n"
                f"আমি আপনার B.Sc. in CSE প্রোগ্রামের একাডেমিক ট্র্যাক পর্যবেক্ষণ করছি "
                f"(বর্তমান CGPA: {cgpa_display}, লক্ষ্যমাত্রা: {target:.2f})।\n\n"
                "পড়াশোনা, রুটিন, পরীক্ষার প্রস্তুতি বা যেকোনো পরামর্শের জন্য আপনার প্রশ্নটি লিখুন!"
            )

        # --- 2. FAREWELL & CONVERSATIONAL ACKNOWLEDGEMENTS ---
        if any(w in q_lower for w in (
            "bye", "tata", "allah hafez", "see you", "good night", "shuvo ratri",
            "pore kotha hobe", "thik ache", "thik ase", "accha", "acha", "bujhlam",
            "ok", "okay", "alhamdulillah", "বিদায়", "আচ্ছা", "ঠিক আছে"
        )):
            return (
                f"You're always welcome, {name}! 🌟\n\n"
                "নিয়মিত পড়াশোনার অভ্যাস বজায় রাখুন এবং ক্লাসের প্রতি মনোযোগী থাকুন। "
                "যেকোনো পড়াশোনার পরিকল্পনা বা সহায়তায় EduTrack AI সবসময় আপনার পাশে আছে!"
            )

        # --- 3. GRATITUDE ---
        if any(w in q_lower for w in ("thank you", "thanks", "dhonnobad", "thx", "onek help hoilo", "অনেক ধন্যবাদ", "ধন্যবাদ")):
            return (
                f"You're very welcome, {name}! 🌟\n\n"
                "আপনার লক্ষ্যমাত্রা অর্জনে নিয়মিত অধ্যবসায় রাখুন। কোনো বিষয়ে সন্দেহ থাকলে নির্দ্বিধায় আমাকে জিজ্ঞেস করুন!"
            )

        # --- 4. IDENTITY & CAPABILITIES ---
        if any(w in q_lower for w in (
            "who are you", "what are you", "what can you do", "tumi ke", "ki korte paro",
            "tumar kaj ki", "introduce yourself", "about yourself", "তুমি কে", "কী করতে পারো", "তোমার কাজ কি"
        )):
            return (
                f"আমি EduTrack AI — আপনার পার্সোনাল একাডেমিক ইন্টেলিজেন্স অ্যাসিস্ট্যান্ট! 🎓\n\n"
                f"আমি আপনার এনরোল করা কোর্স, CGPA রেকর্ড, ক্লাসের শিডিউল ও অ্যাটেনডেন্সের উপর ভিত্তি করে রিয়েল-টাইম অফলাইন বিশ্লেষণ প্রদান করি।\n\n"
                "আমার মূল সক্ষমতাসমূহ:\n"
                f"1. 🎯 Trajectory Planner: আপনার {target:.2f} CGPA লক্ষ্যে পৌঁছাতে সামনের ক্রেডিটগুলোতে গড়ে কত GPA পেতে হবে তা হিসাব করা।\n"
                "2. 📅 7-Day Timetable: ক্লাসের সময়ের সাথে সামঞ্জস্য রেখে সাপ্তাহিক পড়ার ভারসাম্যপূর্ণ রুটিন তৈরি করা।\n"
                "3. 🔄 Retake Simulator: কম গ্রেড পাওয়া কোর্সগুলো রিটেক দিলে কীভাবে দ্রুত CGPA বুস্ট হবে তার সঠিক পূর্বাভাস।\n"
                "4. ⚠️ Attendance Watchdog: কোনো কোর্সে উপস্থিতি ৭৫% এর নিচে নামলে পরীক্ষার আগেই সতর্কবার্তা প্রদান।\n"
                "5. ⚡ Exam Prep & Stress Management: পড়া মনে রাখার অ্যাক্টিভ রিকল টেকনিক এবং স্টাডি প্ল্যানিং।\n\n"
                "যেকোনো প্রশ্ন লিখে এন্টার (Enter) প্রেস করুন!"
            )

        # --- 5. MOTIVATION, STRESS, PROCRASTINATION & FOCUS ---
        if any(w in q_lower for w in (
            "stress", "tension", "tensed", "depressed", "voy", "fear", "fail",
            "mon boshe na", "alashemi", "procrastinat", "motivat", "motivation",
            "tired", "bhalo lagena", "panic", "parbo na", "কষ্ট", "মন বসে না", "টেনশন", "ভয়"
        )):
            return (
                f"💡 ACADEMIC MOTIVATION & FOCUS COACHING ({name})\n\n"
                "সিএসই এবং ইঞ্জিনিয়ারিং পড়াশোনায় মানসিক চাপ বা মনোযোগের ঘাটতি অনুভব করা খুব স্বাভাবিক। তবে মনে রাখবেন:\n\n"
                f"• আপনার বর্তমান ভিত্তি: আপনি ইতিমধ্যে {credits:g} ক্রেডিট সফলভাবে সম্পন্ন করেছেন (CGPA: {cgpa_display})। আপনি অবশ্যই সামনে আরও ভালো করতে সক্ষম।\n\n"
                "📌 মনোযোগ ফিরিয়ে আনার ৩টি গোল্ডেন রুল:\n"
                "1. দ্য ৫-মিনিট রুল: বড় সিলেবাস দেখে ভয় না পেয়ে ভাবুন 'আমি শুধু মাত্র ৫ মিনিট পড়ব/কোড করব'। শুরু করার পরেই পড়ার মোমেন্টাম চলে আসে।\n"
                "2. পোমোডোরো টেকনিক (Pomodoro): ২৫ মিনিট মোবাইল দূরে রেখে সম্পূর্ণ ফোকাস দিয়ে পড়ুন, এরপর ৫ মিনিটের রিফ্রেশিং ব্রেক নিন।\n"
                "3. একটি করে কাজ: একসাথে ৩টি বিষয়ের চিন্তা না করে আজকের সবচেয়ে গুরুত্বপূর্ণ ১টি টপিক শেষ করুন।\n\n"
                "মনে রাখবেন, ধারাবাহিকতাই সেরা সাফল্য এনে দেয়। আজ থেকেই শুরু করুন!"
            )

        # --- 6. PROGRAMMING, PROJECTS & LAB GUIDANCE ---
        if any(w in q_lower for w in (
            "programming", "code", "coding", "python", "java", "c++", "dsa",
            "project", "thesis", "lab", "assignment", "problem solve", "leet code",
            "software", "development", "প্রজেক্ট", "প্রোগ্রামিং", "কোডিং", "অ্যাসাইনমেন্ট"
        )):
            return (
                f"💻 CSE PROGRAMMING & PROJECT STRATEGY ({name})\n\n"
                "সিএসইতে ভালো রেজাল্ট এবং ইন্ডাস্ট্রি স্কিল অর্জনের জন্য থিওরি ও ল্যাবের সমন্বয় অত্যন্ত জরুরি:\n\n"
                "1. ল্যাব রিপোর্ট ও অ্যাসাইনমেন্ট:\n"
                "   - ল্যাব পারফরম্যান্স এবং সময়মত অ্যাসাইনমেন্ট সাবমিশন আপনার সেমিস্টার GPA-এর একটি বড় অংশ নির্ধারণ করে।\n"
                "   - কোড লেখার সময় সবসময় ক্লিন কমেন্ট এবং গিট (Git) দিয়ে ভার্সন কন্ট্রোল বজায় রাখুন।\n\n"
                "2. প্রোগ্রামিং লজিক ডেভেলপমেন্ট:\n"
                "   - মুখস্থ না করে প্রতিদিন কমপক্ষে ১টি করে বেসিক প্রবলেম সলভ করুন (LeetCode/Codeforces/HackerRank)।\n"
                "   - Data Structures & Algorithms (DSA) এবং অবজেক্ট ওরিয়েন্টেড কনসেপ্টে বিশেষ জোর দিন।\n\n"
                "3. ফাইনাল ইয়ার প্রজেক্ট / থিসিস প্রস্তুতি:\n"
                "   - নিজের আগ্রহের ফিল্ড (AI/ML, Web, App, Cyber Security) অনুযায়ী একটি রিয়েল-ওয়ার্ল্ড প্রজেক্ট বেছে নিন।\n\n"
                "আজকের স্টাডি ব্লকে আপনার ল্যাব প্রবলেমগুলো প্র্যাকটিস করার জন্য ১ ঘণ্টা সময় বরাদ্দ রাখুন!"
            )

        # --- 7. ATTENDANCE & CLASS TIMINGS ---
        if any(w in q_lower for w in (
            "attendance", "shortage", "presence", "class skip", "percentage",
            "75%", "clearence", "hazira", "kalke ki class", "class routine", "উপস্থিতি", "হাজিরা", "ক্লাস"
        )):
            lines_att: list[str] = [f"📋 ATTENDANCE STATUS & ACADEMIC CLEARANCE ({name})"]
            if low_attendance:
                lines_att.append("⚠️ ATTENDANCE WARNING (Below 75% Clearance Threshold):")
                for att in low_attendance:
                    pct = att.get('attendance_percentage', 0)
                    lines_att.append(f"• {att.get('course_code', 'Course')}: {pct:.1f}% উপস্থিতি — জরুরি ভিত্তিতে পরবর্তী ক্লাসগুলোতে উপস্থিত থাকতে হবে!")
                lines_att.append("\nবি.দ্র.: বিশ্ববিদ্যালয়ের নীতিমালা অনুযায়ী পরীক্ষায় বসার জন্য ন্যূনতম ৭৫% উপস্থিতি আবশ্যক। অনুপস্থিতির কারণ থাকলে দ্রুত কোর্স শিক্ষকের সাথে যোগাযোগ করুন।")
            else:
                lines_att.append("✅ চমৎকার রেকর্ড! আপনার কোনো কোর্সেই উপস্থিতি ৭৫%-এর নিচে নেই।")
                lines_att.append("ক্লাসে নিয়মিত উপস্থিত থাকলে কন্টিনিউয়াস অ্যাসেসমেন্টে ফুল মার্কস নিশ্চিত করা অনেক সহজ হয়।")
            return "\n".join(lines_att)

        lines: list[str] = []

        # --- SCENARIO 7.5: OFFLINE MACHINE LEARNING & SIMULATION ENGINE ---
        if any(w in q_lower for w in (
            "ml", "machine learning", "algorithm", "simulate", "model", "random forest",
            "prediction", "predict my grade", "how ai works", "offline ai", "xai", "explainable",
            "মেশিন লার্নিং", "অ্যালগরিদম", "প্রেডিকশন"
        )):
            try:
                from modules.offline_ml import AcademicMLPipeline
                pipeline = AcademicMLPipeline.get_instance()
                avg_att = sum(item.get("attendance_percentage", 85.0) for item in attendance) / max(len(attendance), 1)
                pred = pipeline.predict(
                    attendance_pct=avg_att,
                    midterm_pct=80.0,
                    continuous_pct=82.0,
                    credit_weight=3.0,
                    prior_cgpa=float(cgpa or 3.22),
                )
                opt = pipeline.solve_pareto_grade_plan(
                    current_cgpa=float(cgpa or 3.22),
                    completed_credits=credits,
                    target_cgpa=target,
                    remaining_credits=rem_credits,
                )
                imp_str = "\n".join([f"  • {k}: {v}% weight" for k, v in pred['feature_importances'].items()])
                plan_str = "\n".join([f"  • {p['grade']} ({p['grade_point']:.2f} GP): {p['courses_needed']} course(s) — {p['description']}" for p in opt.get('plan', [])])

                return (
                    f"🤖 EDUTRACK ENTERPRISE OFFLINE ML DIAGNOSTIC ({name})\n\n"
                    f"📊 Core Machine Learning Specifications:\n"
                    f"• Algorithm: {pred['meta']['algorithm']}\n"
                    f"• Execution: {pred['meta']['framework']} (Latency: {pred['meta']['latency_ms']}ms, 100% Offline)\n"
                    f"• Course Performance Prediction: {pred['predicted_marks']}% Score → {pred['predicted_grade']} ({pred['predicted_grade_point']:.2f} Grade Point)\n"
                    f"• Risk Classification: {pred['risk_category']} (Critical Risk Probability: {pred['critical_risk_pct']}%)\n\n"
                    f"🔍 Explainable AI (XAI) Attribution Factor:\n{imp_str}\n\n"
                    f"🎯 Pareto-Optimal Target Plan ({target:.2f} CGPA Goal):\n"
                    f"• Required Future Average GPA: {opt['required_avg']:.2f}\n"
                    f"{plan_str}\n\n"
                    f"💡 You can also test custom what-if scenarios in real-time inside the AI Simulation Lab!"
                )
            except Exception:
                pass

        # --- SCENARIO 8: CGPA TARGET & HOW TO REACH GOAL ---
        if any(w in q_lower for w in (
            "cgpa", "goal", "target", "reach", "achieve", "improve", "diagnos",
            "barabo", "bhalo korbo", "barate", "jump", "point", "kivabe cgpa",
            "grade boost", "amar cgpa", "current standing", "সিজিপিএ", "গ্রেড", "টার্গেট"
        )):
            lines.append(f"🎯 ACADEMIC TRAJECTORY DIAGNOSTIC ({name})")
            lines.append(
                f"You have {credits:g} graded credits completed with a current CGPA of {cgpa_display} across {len(courses)} recorded course(s). "
                f"Your saved target is {target:.2f} CGPA across a {prog_credits:g}-credit degree."
            )
            lines.append("")

            if req_gpa is not None:
                if req_gpa <= 0:
                    lines.append(
                        f"🌟 Status: You are already on track! Your current pace exceeds your {target:.2f} target. "
                        "Focus on maintaining your grade stability without burning out."
                    )
                elif req_gpa <= 3.85:
                    lines.append(
                        f"📊 Required Future GPA: You need an average GPA of {req_gpa:.2f} across your remaining {rem_credits:g} credits. "
                        "This goal is realistic and achievable with consistent study routines."
                    )
                elif req_gpa <= 4.00:
                    lines.append(
                        f"⚡ High-Pace Milestone: You need an average GPA of {req_gpa:.2f} across your remaining {rem_credits:g} credits. "
                        "Because this requires near-perfect grades, you should combine strong semester performance with course retakes to reduce the pressure."
                    )
                else:
                    lines.append(
                        f"⚠️ Ceiling Notice: Mathematically reaching {target:.2f} purely from new courses requires {req_gpa:.2f} (above 4.00). "
                        "However, you can still easily achieve this target by retaking earlier lower-grade courses to gain bonus grade points!"
                    )
            lines.append("")
            lines.append("📋 RECOMMENDED STRATEGIC PRIORITIES:")
            if weak_names:
                lines.append(f"• Priority Review: First courses to review: {', '.join(weak_names[:4])}. Allocate 4+ hours weekly to work through problem sets.")
            else:
                lines.append("• Core Mastery: Continue consistent preparation and prioritize your 3-credit lecture courses.")

            if low_attendance:
                low_att_names = [str(i.get("course_code", "Course")) for i in low_attendance[:3]]
                lines.append(f"• Attendance Alert: Attendance below 75% needs attention in: {', '.join(low_att_names)}. Regular attendance directly protects your continuous assessment marks.")
            else:
                lines.append("• Attendance Record: No recorded course has attendance below 75%. Keep this high standard.")

            lines.append("• Retake Advantage: Use the Trajectory Planner Retake Simulator to calculate the exact jump you can achieve by repeating low-grade courses.")

        # --- SCENARIO 9: 7-DAY STUDY TIMETABLE & ROUTINE ---
        elif any(w in q_lower for w in (
            "routine", "schedule", "timetable", "weekly", "plan", "time table",
            "porar", "study time", "kivabe porbo", "shomoy paina", "time management",
            "daily plan", "study schedule", "routine dao", "রুটিন", "পড়ার সময়", "পড়াশোনা"
        )):
            lines.append(f"📅 PERSONALIZED 7-DAY STUDY TIMETABLE ({name})")
            lines.append(
                f"Based on your profile ({credits:g} graded credits, current CGPA {cgpa_display}), "
                "here is a structured weekly training plan designed to balance lectures, active recall, and rest:"
            )
            lines.append("")
            lines.append("• Monday – Thursday (Lecture Alignment & Problem Solving):")
            lines.append("  - 05:00 PM – 06:30 PM: Deep Focus Block — Review today's lecture slides and solve 2-3 worked exercises.")
            lines.append("  - 07:30 PM – 08:45 PM: Active Recall — Summarize core concepts without looking at lecture notes.")
            lines.append("")
            lines.append("• Friday (Lab & Project Sprint):")
            lines.append("  - 03:00 PM – 05:30 PM: Programming assignments, lab reports, and coursework implementation.")
            lines.append("")
            lines.append("• Saturday (Concept Consolidation):")
            lines.append("  - 10:00 AM – 12:30 PM: Dedicated review for challenging subjects (focusing on low-grade or high-credit courses).")
            lines.append("")
            lines.append("• Sunday (Assessment & Weekly Reset):")
            lines.append("  - 04:00 PM – 05:30 PM: 30-minute self-test and organizing goals for the upcoming week.")
            lines.append("")
            if low_attendance:
                lines.append("⚠️ ATTENDANCE NOTE:")
                low_att_names = [str(i.get("course_code", "Course")) for i in low_attendance[:3]]
                lines.append(f"Attendance below 75% needs attention in: {', '.join(low_att_names)}. Never skip upcoming sessions.")

        # --- SCENARIO 10: RETAKE STRATEGY ---
        elif any(w in q_lower for w in (
            "retake", "repeat", "improve", "replacement", "c grade", "d grade",
            "f grade", "course repeat", "retake strategy", "retake ki", "retake korbo",
            "retake dibo", "আগের কোর্স", "রিটেক"
        )):
            lines.append(f"🔄 COURSE RETAKE STRATEGY & IMPACT ANALYSIS ({name})")
            lines.append(
                f"You currently have {credits:g} graded credits. Retaking an earlier course with a low grade allows you to replace "
                "the previous grade point with a higher one, boosting your CGPA without adding extra credit burden."
            )
            lines.append("")
            lines.append("💡 RETAKE SELECTION RULES:")
            lines.append("1. Target 3-Credit Courses First: A 3-credit course has three times the weight of a 1-credit lab.")
            lines.append("2. Replace C/D Grades: Improving a course from C (2.25) to A (3.75) adds +4.5 grade points directly to your cumulative total.")
            if weak_names:
                lines.append(f"3. Identified Courses: First courses to review for retake: {', '.join(weak_names[:4])}.")
            lines.append("")
            lines.append("📌 ACTION STEP:")
            lines.append("Open the Trajectory Planner in EduTrack and test different target grades in the Retake Simulator to see your exact CGPA jump.")

        # --- SCENARIO 11: EXAM PREPARATION ---
        elif any(w in q_lower for w in (
            "exam", "test", "final", "midterm", "prep", "preparation", "porashuna",
            "study tips", "active recall", "pomodoro", "quiz", "fail", "shob bhule jai",
            "পরীক্ষা", "প্রস্তুতি"
        )):
            lines.append(f"⚡ HIGH-YIELD EXAM PREPARATION FRAMEWORK ({name})")
            lines.append("Follow this structured 3-phase preparation sequence to maximize your grade band:")
            lines.append("")
            lines.append("1. Phase 1 — Topic Triage (2 Weeks Before Exam):")
            lines.append("   - Classify syllabus topics into Green (Confident), Yellow (Needs Practice), and Red (Challenging).")
            lines.append("   - Spend 70% of your initial study blocks converting Red topics to Yellow.")
            lines.append("")
            lines.append("2. Phase 2 — Active Recall & Mock Tests (1 Week Before):")
            lines.append("   - Practice timed questions from previous term papers.")
            lines.append("   - Never re-read passively: close the textbook and write out formulas or definitions from memory.")
            lines.append("")
            lines.append("3. Phase 3 — Pre-Exam Consolidation (48 Hours Before):")
            lines.append("   - Focus strictly on formula sheets, high-frequency concepts, and error logs.")
            lines.append("   - Prioritize 7+ hours of sleep to ensure cognitive peak on exam day.")
            if low_attendance:
                low_att_names = [str(i.get("course_code", "Course")) for i in low_attendance[:3]]
                lines.append(f"\n⚠️ Exam Clearance Alert: Attendance below 75% needs attention in: {', '.join(low_att_names)}. Ensure clearance with your department controller.")

        # --- SCENARIO 12: INTELLIGENT DYNAMIC FALLBACK FOR ALL OTHER QUERIES ---
        else:
            lines.append(f"🤖 EDUTRACK AI ACADEMIC ADVISOR ({name})")
            lines.append(f"আপনার প্রশ্ন: \"{question.strip()}\"")
            lines.append("")
            lines.append(
                f"আপনার একাডেমিক রেকর্ড অনুসারে বর্তমানে CGPA {cgpa_display} এবং {credits:g} ক্রেডিট সম্পন্ন হয়েছে (টার্গেট: {target:.2f})।"
            )
            lines.append("")
            lines.append("💡 একাডেমিক নির্দেশনা ও কার্যপদ্ধতি:")
            if weak_names:
                lines.append(f"1. প্রায়োরিটি সাবজেক্ট: আপনার পূর্ববর্তী কোর্সগুলোর মধ্যে {', '.join(weak_names[:3])}-এর মতো বিষয়ে বিশেষ নজর দিন।")
            else:
                lines.append("1. ধারাবাহিক অধ্যয়ন: প্রতিদিনের ক্লাসের পড়া সেদিনই রিভিশন দেওয়ার অভ্যাস বজায় রাখুন।")
            
            if low_attendance:
                low_att_names = [str(i.get("course_code", "Course")) for i in low_attendance[:2]]
                lines.append(f"2. অ্যাটেনডেন্স সতর্কতা: {', '.join(low_att_names)} কোর্সে উপস্থিতি ৭৫%-এর নিচে, তাই সামনের কোনো ক্লাস মিস করবেন না।")
            else:
                lines.append("2. অ্যাটেনডেন্স স্ট্যান্ডার্ড: আপনার উপস্থিতি সন্তোষজনক, এই ধারাবাহিকতা ধরে রাখুন।")

            lines.append("3. নিয়মিত প্র্যাকটিস: প্রতিদিন ৪৫ মিনিটের ফোকাসড সেশনে অ্যাক্টিভ রিকল বা কোডিং প্র্যাকটিস করুন।")
            lines.append("")
            lines.append("📌 আপনি চাইলে নির্দিষ্টভাবে জিজ্ঞেস করতে পারেন:")
            lines.append("• \"How to reach my target CGPA?\" (টার্গেট অর্জনের সুনির্দিষ্ট ক্যালকুলেশন)")
            lines.append("• \"7-Day Study Timetable\" (সাপ্তাহিক রুটিন)")
            lines.append("• \"Retake Strategy\" (রিটেক কোর্সের হিসাব ও সিমুলেশন)")
            lines.append("• \"Exam Preparation Tips\" (পরীক্ষার সেরা রিভিশন কৌশল)")

        return "\n".join(lines)
