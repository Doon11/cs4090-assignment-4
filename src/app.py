import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import pytest
import sys, io, os
from datetime import datetime
from tasks import load_tasks, save_tasks, filter_tasks_by_priority, filter_tasks_by_category, generate_unique_id

def main():
    st.title("To-Do Application")
    
    # Load existing tasks
    tasks = load_tasks()
    
    # Sidebar tabs for adding new tasks or running pytests
    add_task_tab, run_test_tab = st.sidebar.tabs(["Add Tasks", "Run Tests"])

    # Task creation form
    with add_task_tab.form("new_task_form"):
        task_title = st.text_input("Task Title")
        task_description = st.text_area("Description")
        task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        task_category = st.selectbox("Category", ["Work", "Personal", "School", "Other"])
        task_due_date = st.date_input("Due Date")
        submit_button = st.form_submit_button("Add Task")
        
        if submit_button and task_title:
            new_task = {
                "id": generate_unique_id(tasks),
                "title": task_title,
                "description": task_description,
                "priority": task_priority,
                "category": task_category,
                "due_date": task_due_date.strftime("%Y-%m-%d"),
                "completed": False,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            tasks.append(new_task)
            save_tasks(tasks)
            st.sidebar.success("Task added successfully!")

    with run_test_tab:
        test_basic = st.button("Run basic tests")
        test_advanced = st.button("Run advanced tests")
        test_tdd = st.button("Run tdd tests")
        test_bdd = st.button("Run bdd tests")
        test_property = st.button("Run property tests")
        html_cov_report = st.button("HTML Coverage Report")
        
        if test_basic:
            output = capture_pytest_stdio(["-v", "tests/test_basic.py", "src/"])
            test_dialog(output)

        if test_advanced:
            output = capture_pytest_stdio(["-v", "tests/test_advanced.py"])
            test_dialog(output)
        
        if test_tdd:
            st.sidebar.error("Not implemented!")

        if test_bdd:
            st.sidebar.error("Not implemented!")
        
        if test_property:
            output = capture_pytest_stdio(["-v", "tests/test_property.py"])
            test_dialog(output)

        if html_cov_report:
            output = capture_pytest_stdio(["--cov=src", "--cov-report=html", "tests/"])
            html_dialog(output)

    # Main area to display tasks
    st.header("Your Tasks")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + list(set([task["category"] for task in tasks])))
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
    
    show_completed = st.checkbox("Show Completed Tasks")
    
    # Apply filters
    filtered_tasks = tasks.copy()
    if filter_category != "All":
        filtered_tasks = filter_tasks_by_category(filtered_tasks, filter_category)
    if filter_priority != "All":
        filtered_tasks = filter_tasks_by_priority(filtered_tasks, filter_priority)
    if not show_completed:
        filtered_tasks = [task for task in filtered_tasks if not task["completed"]]
    
    # Display tasks
    for task in filtered_tasks:
        col1, col2 = st.columns([4, 1])
        with col1:
            if task["completed"]:
                st.markdown(f"~~**{task['title']}**~~")
            else:
                st.markdown(f"**{task['title']}**")
            st.write(task["description"])
            st.caption(f"Due: {task['due_date']} | Priority: {task['priority']} | Category: {task['category']}")
        with col2:
            if st.button("Complete" if not task["completed"] else "Undo", key=f"complete_{task['id']}"):
                for t in tasks:
                    if t["id"] == task["id"]:
                        t["completed"] = not t["completed"]
                        save_tasks(tasks)
                        st.rerun()
            if st.button("Delete", key=f"delete_{task['id']}"):
                tasks = [t for t in tasks if t["id"] != task["id"]]
                save_tasks(tasks)
                st.rerun()


@st.dialog("Test Results:", width="large")
def test_dialog(results):
    st.write(results)


@st.dialog("Coverage Report:", width="large")
def html_dialog(results):
    st.write(results)
    report_filename = "./htmlcov/index.html"
    with open(report_filename, 'r') as file:
        content = file.read()
        tables = pd.read_html(io.StringIO(content))
        df = tables[0]
        st.dataframe(df)


def capture_pytest_stdio(args):
    base_stdout = sys.stdout
    capture = io.StringIO()
    sys.stdout = capture
    os.environ["PYTHONPATH"] = "src"
    with st.spinner("Running test..."):
        pytest.main(args)
    sys.stdout = base_stdout
    return capture.getvalue()


if __name__ == "__main__":
    main()