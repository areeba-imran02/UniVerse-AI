import streamlit as st, json
from services.auth import init_db, create_user, authenticate_user, get_user_by_email, update_password, validate_password, normalize_email
from services.storage import list_projects, save_project, delete_project
from services.ai import run_agent_task
from services.visuals import render_result_visuals

st.set_page_config(page_title="UniVerse AI", page_icon="✦", layout="wide")
init_db()
st.markdown("""<style>
.stApp{background:linear-gradient(135deg,#f7faf5,#edf5ed 60%,#f4f8f1);color:#20312b}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#183f34,#245b49)}
[data-testid="stSidebar"] *{color:#f4f8f1!important}
h1,h2,h3{color:#203d32;letter-spacing:-.03em}
.brand{font-size:1.05rem;font-weight:800;letter-spacing:.04em;color:#18765a}
.hero{font-size:2.6rem;line-height:1.08;font-weight:800;color:#203d32}
.subtle{color:#687a70}
.panel{background:rgba(255,255,255,.86);border:1px solid #e1eae0;border-radius:22px;padding:24px;box-shadow:0 14px 45px #1d43310d}
.stButton>button{border-radius:12px;min-height:2.7rem;font-weight:650}
.stButton>button[kind="primary"]{background:#18765a;border-color:#18765a;color:white}
div[data-testid="stForm"]{background:#ffffffd9;padding:22px;border:1px solid #e1eae0;border-radius:20px}
</style>""", unsafe_allow_html=True)

st.session_state.setdefault("user", None)
st.session_state.setdefault("auth_view", "login")
st.session_state.setdefault("active_page", "Dashboard")
st.session_state.setdefault("active_project", None)

def go(view):
    st.session_state.auth_view=view
    st.rerun()

def logout():
    for k in list(st.session_state.keys()):
        if k not in []: del st.session_state[k]
    st.session_state.user=None
    st.session_state.auth_view="login"
    st.session_state.active_page="Dashboard"
    st.rerun()

def auth_screen():
    left,right=st.columns([1.05,.95],gap="large")
    with left:
        st.markdown('<div class="brand">✦ UNIVERSE AI</div><br><div class="hero">Ideas into insight.<br>Insight into action.</div><p class="subtle">A focused workspace for learning, research, engineering and intelligent project work.</p>',unsafe_allow_html=True)
        st.markdown('<div class="panel"><h3>One workspace. Many disciplines.</h3><p class="subtle">Plan tasks, explore concepts, run calculations and keep your work organized.</p></div>',unsafe_allow_html=True)
    with right:
        view=st.session_state.auth_view
        if view=="login":
            st.markdown("## Welcome back")
            st.caption("Sign in to continue to your workspace.")
            with st.form("login"):
                email=st.text_input("Email address",placeholder="you@example.com")
                password=st.text_input("Password",type="password",placeholder="Enter your password")
                remember=st.checkbox("Remember me on this browser")
                submitted=st.form_submit_button("Log in",type="primary",use_container_width=True)
            a,b=st.columns(2)
            if a.button("Forgot password?",use_container_width=True): go("forgot")
            if b.button("Create account",use_container_width=True): go("signup")
            if submitted:
                if not email.strip() or not password: st.error("Enter both your email and password.")
                else:
                    user=authenticate_user(email,password)
                    if user:
                        st.session_state.user=user; st.session_state.auth_view=None; st.session_state.active_page="Dashboard"; st.session_state.remember_me=remember; st.rerun()
                    else: st.error("The email or password is incorrect.")
        elif view=="signup":
            st.markdown("## Create your account")
            st.caption("Start building your personal AI workspace.")
            with st.form("signup",clear_on_submit=True):
                name=st.text_input("Full name")
                email=st.text_input("Email address",placeholder="you@example.com")
                password=st.text_input("Password",type="password",help="10+ characters, uppercase, lowercase, number and symbol")
                confirm=st.text_input("Confirm password",type="password")
                submitted=st.form_submit_button("Create account",type="primary",use_container_width=True)
            if submitted:
                clean_email=normalize_email(email)
                err=None
                if len(name.strip())<2: err="Enter your full name (at least 2 characters)."
                elif "@" not in clean_email or "." not in clean_email.split("@")[-1]: err="Enter a valid email address."
                elif password!=confirm: err="The passwords do not match."
                else: err=validate_password(password)
                if err: st.error(err)
                else:
                    try:
                        st.session_state.user=create_user(name,clean_email,password); st.session_state.auth_view=None; st.session_state.active_page="Dashboard"; st.rerun()
                    except ValueError as e: st.error(str(e))
                    except Exception: st.error("Account creation failed. Please try again.")
            if st.button("← Back to login",use_container_width=True): go("login")
        else:
            st.markdown("## Reset your password")
            st.warning("Email verification is not configured in this starter. Do not expose this reset flow publicly before replacing it with an emailed, expiring reset token.")
            with st.form("forgot"):
                email=st.text_input("Account email")
                password=st.text_input("New password",type="password")
                confirm=st.text_input("Confirm new password",type="password")
                submitted=st.form_submit_button("Update password",type="primary",use_container_width=True)
            if submitted:
                user=get_user_by_email(email)
                if not user: st.error("No account was found for that email.")
                elif password!=confirm: st.error("The passwords do not match.")
                else:
                    err=validate_password(password)
                    if err: st.error(err)
                    else: update_password(user["id"],password); st.success("Password updated. Please log in."); go("login")
            if st.button("← Back to login",use_container_width=True): go("login")

def sidebar(u):
    with st.sidebar:
        st.markdown("## ✦ UniVerse AI")
        st.caption("INTELLIGENT WORKSPACE")
        st.divider()
        for p in ["Dashboard","AI Workspace","My Projects","Study Tools","Settings"]:
            if st.button(("◈  " if st.session_state.active_page==p else "○  ")+p,key="nav"+p,use_container_width=True):
                st.session_state.active_page=p; st.rerun()
        st.divider(); st.markdown("**"+u["full_name"]+"**"); st.caption(u["email"])
        if st.button("Log out",use_container_width=True): logout()
        st.caption("Projects are private to your account.")

def dashboard(u):
    st.caption("YOUR PERSONAL AI WORKSPACE")
    st.markdown(f"### Good to see you, {u['full_name'].split()[0]} 👋")
    st.title("Your ideas, in motion.")
    st.write("Explore a question, build a project, or work through a discipline-specific task.")
    ps=list_projects(u["id"])
    a,b,c=st.columns(3)
    a.metric("Saved projects",len(ps)); b.metric("Discipline categories",11); c.metric("Workspace access","Private")
    st.markdown("### Start working")
    x,y,z=st.columns(3)
    for col,title,desc,discipline in [
        (x,"💻 Computer Science & IT","Programming, cybersecurity, data and software design.","Computer Science & IT"),
        (y,"⚙️ Engineering","Calculations, systems and design problems.","Engineering"),
        (z,"🩺 Medical Education Simulation","Learning scenarios and concept explanations.","Medical Education Simulation")]:
        with col:
            st.markdown('<div class="panel">',unsafe_allow_html=True); st.markdown("#### "+title); st.caption(desc)
            if st.button("Open workspace",key="dash"+discipline,type="primary",use_container_width=True):
                st.session_state.active_page="AI Workspace"; st.session_state.preselected=discipline; st.rerun()
            st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("### Recent projects")
    if not ps: st.info("Your saved projects will appear here after your first task.")
    for p in ps[:5]:
        with st.container(border=True):
            c1,c2=st.columns([4,1]); c1.markdown("**"+p["title"]+"**"); c1.caption(p["discipline"]+" · "+p["created_at"])
            if c2.button("Open",key="recent"+str(p["id"])):
                st.session_state.active_project=p["id"]; st.session_state.active_page="My Projects"; st.rerun()
    if st.button("＋ New project",type="primary"): st.session_state.active_page="AI Workspace"; st.rerun()

def workspace(u):
    st.title("AI Agent Workspace")
    st.caption("Describe your task. The workflow organizes the request, generates a response and saves the result.")
    ds=["Computer Science & IT","Engineering","Medical Education Simulation","Mathematics","Physics","Business & Economics","Writing & Communication","Data Science","Cybersecurity","General Research","Other"]
    default=st.session_state.pop("preselected",ds[0])
    with st.form("task"):
        title=st.text_input("Project title",placeholder="e.g. Explain Python identity operators")
        discipline=st.selectbox("Discipline",ds,index=ds.index(default) if default in ds else 0)
        kind=st.selectbox("Task type",["Explain a concept","Solve a problem","Create a study plan","Analyze information","Write or improve content","Generate code","Research and compare"])
        prompt=st.text_area("Task details",placeholder="Include your question, context, requirements and desired output...",height=170)
        file=st.file_uploader("Optional supporting file",type=["txt","md","csv","json","py"])
        run=st.form_submit_button("Run agent workflow",type="primary",use_container_width=True)
    if run:
        if len(prompt.strip())<8: st.error("Please describe your task in a little more detail."); return
        attachment=file.getvalue().decode("utf-8",errors="replace")[:20000] if file else ""
        with st.spinner("Working through the task..."):
            result=run_agent_task(prompt,discipline,kind,attachment)
            pid=save_project(u["id"],title.strip() or prompt.strip().splitlines()[0][:80],discipline,kind,prompt,result)
        st.session_state.last_result=result; st.session_state.last_project_id=pid
        st.success("Workflow finished and project saved.")
    if "last_result" in st.session_state:
        r=st.session_state.last_result
        t1,t2,t3=st.tabs(["Answer","Workflow","Visuals & export"])
        with t1:
            st.markdown(r.get("answer","No answer generated."))
            if r.get("limitations"): st.warning("Limitations: "+" ".join(r["limitations"]))
        with t2:
            for s in r.get("stages",[]):
                with st.expander(s["name"]): st.write(s["summary"])
        with t3:
            render_result_visuals(r)
            st.download_button("Download JSON",json.dumps(r,indent=2,ensure_ascii=False),"universe_result.json","application/json")
            st.download_button("Download Markdown","# UniVerse AI Result\n\n"+r.get("answer",""),"universe_result.md","text/markdown")

def projects_page(u):
    st.title("My Projects"); st.caption("Only projects belonging to your account appear here.")
    ps=list_projects(u["id"])
    if not ps:
        st.info("No saved projects yet.")
        if st.button("Start a task",type="primary"): st.session_state.active_page="AI Workspace"; st.rerun()
        return
    for p in ps:
        with st.container(border=True):
            a,b=st.columns([4,1]); a.markdown("### "+p["title"]); a.caption(f'{p["discipline"]} · {p["task_type"]} · {p["created_at"]}')
            if b.button("Open / close",key="openclose"+str(p["id"])):
                st.session_state.active_project=None if st.session_state.active_project==p["id"] else p["id"]; st.rerun()
            if st.session_state.active_project==p["id"]:
                st.markdown(p["result"].get("answer",""))
                with st.expander("Workflow details"):
                    for s in p["result"].get("stages",[]): st.markdown(f'**{s["name"]}** — {s["summary"]}')
                st.download_button("Export JSON",json.dumps(p["result"],indent=2),"project.json",key="exp"+str(p["id"]))
            if st.button("Delete project",key="del"+str(p["id"])):
                st.session_state.confirm_delete=p["id"]
            if st.session_state.get("confirm_delete")==p["id"]:
                st.warning("Delete this project permanently?")
                c1,c2=st.columns(2)
                if c1.button("Confirm delete",key="confirm"+str(p["id"]),type="primary"):
                    delete_project(u["id"],p["id"]); st.session_state.pop("confirm_delete",None); st.rerun()
                if c2.button("Cancel",key="cancel"+str(p["id"])):
                    st.session_state.pop("confirm_delete",None); st.rerun()

def study_tools(u):
    st.title("Study Tools")
    t1,t2,t3=st.tabs(["Study plan","Quick calculator","Flashcards"])
    with t1:
        with st.form("plan"):
            subject=st.text_input("Subject or exam",placeholder="Cybersecurity fundamentals")
            days=st.slider("Days available",1,30,7); hours=st.slider("Study hours per day",1,8,2)
            submit=st.form_submit_button("Create study plan",type="primary")
        if submit:
            prompt=f"Create a practical {days}-day study plan for {subject}, with {hours} hours each day, active recall, practice and revision."
            r=run_agent_task(prompt,"Education","Create a study plan",""); st.markdown(r["answer"]); save_project(u["id"],f"{subject or 'Study plan'} ({days} days)","Education","Create a study plan",prompt,r)
    with t2:
        st.write("Ohm's law: I = V / R")
        v=st.number_input("Voltage (V)",min_value=0.0,value=12.0,step=1.0); r=st.number_input("Resistance (Ω)",min_value=.01,value=6.0,step=1.0)
        if st.button("Calculate current",type="primary"): st.metric("Current",f"{v/r:.3f} A")
    with t3:
        topic=st.text_input("Topic for flashcards")
        if st.button("Generate flashcards",type="primary"):
            if len(topic.strip())<2: st.warning("Enter a topic first.")
            else:
                prompt=f"Create 8 concise study flashcards about {topic}. Format as Question / Answer pairs."
                r=run_agent_task(prompt,"Education","Study flashcards",""); st.markdown(r["answer"]); save_project(u["id"],"Flashcards: "+topic,"Education","Study flashcards",prompt,r)

def settings(u):
    st.title("Settings & Profile")
    st.text_input("Full name",u["full_name"],disabled=True); st.text_input("Email",u["email"],disabled=True)
    st.markdown("### Gemini AI configuration")
    st.caption("Add a key in Streamlit Community Cloud → App settings → Secrets.")
    st.code('GEMINI_API_KEY = "your-key-here"',language="toml")
    st.markdown("### Session")
    st.write("Signed-in workspace session uses Streamlit session state.")
    if st.button("Log out",type="primary"): logout()

if st.session_state.user is None:
    auth_screen()
else:
    user=st.session_state.user; sidebar(user)
    {"Dashboard":dashboard,"AI Workspace":workspace,"My Projects":projects_page,"Study Tools":study_tools,"Settings":settings}[st.session_state.active_page](user)
