import streamlit as st
import time
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="WFH Inactivity Detector",
    page_icon="💼",
    layout="wide"
)

# ============================================================================
# CONSTANTS - Inactivity Thresholds (in seconds)
# ============================================================================
ACTIVE_THRESHOLD = 60        # < 1 minute = Active
SHORT_BREAK_THRESHOLD = 300  # 1-5 minutes = Short Break
                             # > 5 minutes = Extended Inactivity

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
# Initialize all session state variables on first run
if 'session_started' not in st.session_state:
    st.session_state.session_started = False
    st.session_state.session_start_time = None
    st.session_state.last_interaction_time = None
    st.session_state.total_active_time = 0.0
    st.session_state.total_inactive_time = 0.0
    st.session_state.interaction_count = 0
    st.session_state.activity_log = []

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_time(seconds):
    """
    Convert seconds to HH:MM:SS format
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted time string (HH:MM:SS)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_activity_status(inactive_seconds):
    """
    Classify activity status based on inactivity duration
    
    Args:
        inactive_seconds: Time since last interaction in seconds
    
    Returns:
        tuple: (status_text, status_color, emoji)
    """
    if inactive_seconds < ACTIVE_THRESHOLD:
        return "Active", "green", "🟢"
    elif inactive_seconds < SHORT_BREAK_THRESHOLD:
        return "Short Break", "orange", "🟡"
    else:
        return "Extended Inactivity", "red", "🔴"


def start_work_session():
    """
    Initialize a new work session
    Resets all counters and starts tracking
    """
    current_time = time.time()
    st.session_state.session_started = True
    st.session_state.session_start_time = current_time
    st.session_state.last_interaction_time = current_time
    st.session_state.total_active_time = 0.0
    st.session_state.total_inactive_time = 0.0
    st.session_state.interaction_count = 1
    st.session_state.activity_log = [{
        'timestamp': datetime.now().strftime("%I:%M:%S %p"),
        'action': 'Session Started',
        'status': 'Active'
    }]


def end_work_session():
    """
    End the current work session
    Clears all session data
    """
    st.session_state.session_started = False
    st.session_state.session_start_time = None
    st.session_state.last_interaction_time = None


def register_interaction(action_description):
    """
    Record user interaction and update activity metrics
    
    Args:
        action_description: Description of what action user performed
    """
    current_time = time.time()
    
    # Calculate time gap since last interaction
    if st.session_state.last_interaction_time:
        time_gap = current_time - st.session_state.last_interaction_time
        
        # Classify the time gap and update counters
        if time_gap < ACTIVE_THRESHOLD:
            st.session_state.total_active_time += time_gap
            status = "Active"
        elif time_gap < SHORT_BREAK_THRESHOLD:
            st.session_state.total_inactive_time += time_gap
            status = "Short Break"
        else:
            st.session_state.total_inactive_time += time_gap
            status = "Extended Inactivity"
        
        # Add entry to activity log
        st.session_state.activity_log.append({
            'timestamp': datetime.now().strftime("%I:%M:%S %p"),
            'action': action_description,
            'status': status,
            'gap': format_time(time_gap)
        })
    
    # Update last interaction time and increment counter
    st.session_state.last_interaction_time = current_time
    st.session_state.interaction_count += 1


# ============================================================================
# MAIN UI LAYOUT
# ============================================================================

# Header Section
st.title("💼 Work From Home Inactivity Detection System")
st.markdown("**Monitor your work activity and stay productive!**")
st.markdown("---")

# Information Section
with st.expander("ℹ️ How It Works", expanded=False):
    st.write("""
    **This system tracks your work activity based on your interactions:**
    
    🟢 **Active** - You're interacting frequently (< 1 minute gaps)
    
    🟡 **Short Break** - Small break detected (1-5 minutes of inactivity)
    
    🔴 **Extended Inactivity** - Long period without activity (> 5 minutes)
    
    **Steps to Use:**
    1. Click "Start Work Session" to begin tracking
    2. Interact regularly by clicking buttons or logging tasks
    3. Monitor your real-time activity status
    4. Review your productivity statistics
    5. Click "End Session" when you finish work
    """)

st.markdown("---")

# ============================================================================
# SESSION CONTROL BUTTONS
# ============================================================================
col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    if not st.session_state.session_started:
        if st.button("🚀 Start Work Session", type="primary", use_container_width=True):
            start_work_session()
            st.success("✅ Work session started!")
            time.sleep(0.5)
            st.rerun()
    else:
        if st.button("🛑 End Session", type="secondary", use_container_width=True):
            end_work_session()
            st.info("Session ended. Start a new session to continue tracking.")
            time.sleep(0.5)
            st.rerun()

with col2:
    if st.session_state.session_started:
        if st.button("✅ Quick Check-in", use_container_width=True):
            register_interaction("Quick Check-in")
            st.rerun()

# ============================================================================
# MAIN CONTENT - Only show when session is active
# ============================================================================
if st.session_state.session_started:
    
    # Calculate current metrics
    current_time = time.time()
    total_session_time = current_time - st.session_state.session_start_time
    time_since_last_interaction = current_time - st.session_state.last_interaction_time
    current_status, status_color, status_emoji = get_activity_status(time_since_last_interaction)
    
    # ========================================================================
    # REAL-TIME STATUS DISPLAY
    # ========================================================================
    st.markdown("### 📊 Current Status")
    
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        st.metric(
            label="Activity Status",
            value=f"{status_emoji} {current_status}"
        )
    
    with status_col2:
        st.metric(
            label="Idle Time",
            value=format_time(time_since_last_interaction)
        )
    
    with status_col3:
        st.metric(
            label="Total Interactions",
            value=st.session_state.interaction_count
        )
    
    st.markdown("---")
    
    # ========================================================================
    # SESSION STATISTICS
    # ========================================================================
    st.markdown("### 📈 Session Statistics")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric(
            label="Total Session Time",
            value=format_time(total_session_time)
        )
    
    with stat_col2:
        st.metric(
            label="Active Time",
            value=format_time(st.session_state.total_active_time)
        )
    
    with stat_col3:
        st.metric(
            label="Inactive Time",
            value=format_time(st.session_state.total_inactive_time)
        )
    
    with stat_col4:
        # Calculate productivity percentage
        if total_session_time > 0:
            productivity = (st.session_state.total_active_time / total_session_time) * 100
        else:
            productivity = 0
        st.metric(
            label="Productivity %",
            value=f"{productivity:.1f}%"
        )
    
    # Progress Bars for Time Distribution
    st.markdown("#### Time Distribution")
    
    prog_col1, prog_col2 = st.columns(2)
    
    with prog_col1:
        if total_session_time > 0:
            active_percent = st.session_state.total_active_time / total_session_time
        else:
            active_percent = 0
        st.progress(active_percent, text=f"🟢 Active: {active_percent*100:.1f}%")
    
    with prog_col2:
        if total_session_time > 0:
            inactive_percent = st.session_state.total_inactive_time / total_session_time
        else:
            inactive_percent = 0
        st.progress(inactive_percent, text=f"🔴 Inactive: {inactive_percent*100:.1f}%")
    
    st.markdown("---")
    
    # ========================================================================
    # INTERACTION PANEL
    # ========================================================================
    st.markdown("### 💬 Log Your Activity")
    
    interact_col1, interact_col2 = st.columns([3, 2])
    
    with interact_col1:
        # Text input for custom task logging
        task_input = st.text_input(
            "What are you working on?",
            placeholder="e.g., Writing report, Coding feature, Client meeting...",
            key="task_input"
        )
        
        if st.button("📝 Log Task", use_container_width=True):
            if task_input.strip():
                register_interaction(f"Task: {task_input}")
                st.success(f"✅ Logged: {task_input}")
                time.sleep(0.5)
                st.rerun()
            else:
                st.warning("⚠️ Please enter a task description")
    
    with interact_col2:
        st.markdown("**Quick Actions:**")
        
        # Quick action buttons in 2x2 grid
        quick_col1, quick_col2 = st.columns(2)
        
        with quick_col1:
            if st.button("☕ Coffee", use_container_width=True):
                register_interaction("Coffee Break")
                st.rerun()
            
            if st.button("📧 Email", use_container_width=True):
                register_interaction("Checking Email")
                st.rerun()
        
        with quick_col2:
            if st.button("📞 Meeting", use_container_width=True):
                register_interaction("In Meeting")
                st.rerun()
            
            if st.button("📚 Reading", use_container_width=True):
                register_interaction("Reading/Research")
                st.rerun()
    
    st.markdown("---")
    
    # ========================================================================
    # ACTIVITY LOG
    # ========================================================================
    st.markdown("### 📋 Activity Log")
    
    if len(st.session_state.activity_log) > 0:
        # Display recent activities (last 15 entries, newest first)
        recent_logs = st.session_state.activity_log[-15:][::-1]
        
        # Create a formatted display
        for log in recent_logs:
            status_emoji_log = "🟢" if log['status'] == "Active" else "🟡" if log['status'] == "Short Break" else "🔴"
            gap_text = f" | Gap: {log['gap']}" if 'gap' in log else ""
            
            st.text(f"{log['timestamp']} {status_emoji_log} {log['status']:20} | {log['action']}{gap_text}")
        
        if len(st.session_state.activity_log) > 15:
            st.caption(f"📌 Showing last 15 of {len(st.session_state.activity_log)} total activities")
    else:
        st.info("👆 No activities logged yet. Start interacting to build your activity log!")
    
    # Auto-refresh every second to update time displays
    time.sleep(1)
    st.rerun()

else:
    # ========================================================================
    # WELCOME SCREEN (when no session is active)
    # ========================================================================
    st.info("👆 Click **'Start Work Session'** button above to begin tracking your work activity")
    
    st.markdown("### 🎯 Key Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        **📊 Real-Time Tracking**
        - Live activity status updates
        - Instant feedback on productivity
        - Continuous time monitoring
        """)
    
    with feature_col2:
        st.markdown("""
        **🎨 Smart Classification**
        - Active work periods
        - Short break detection
        - Extended inactivity alerts
        """)
    
    with feature_col3:
        st.markdown("""
        **📈 Detailed Analytics**
        - Session statistics
        - Productivity percentage
        - Complete activity logs
        """)
    
    st.markdown("---")
    
    st.markdown("### 🔒 Privacy First")
    st.success("""
    ✅ No webcam or microphone access
    
    ✅ No screen recording or screenshots
    
    ✅ Simple interaction-based tracking
    
    ✅ Complete transparency in monitoring
    """)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption("💼 WFH Inactivity Detection System | Built with Streamlit")