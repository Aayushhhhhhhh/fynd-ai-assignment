import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
import requests

st.set_page_config(page_title="Feedback System", page_icon="⭐", layout="wide")

DATA_FILE = 'feedback_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_user_response(rating, review):
    if rating >= 4:
        return f"Thank you so much for your {rating}-star review! We're thrilled you had a great experience. Your feedback motivates our entire team!"
    elif rating == 3:
        return f"Thank you for your {rating}-star feedback. We appreciate your honest review and will work on improving your experience next time."
    else:
        return f"We sincerely apologize for your {rating}-star experience. This is not the standard we set for ourselves. Our manager will contact you shortly to make things right."

def generate_summary(rating, review):
    words = review.split()[:12]
    return " ".join(words) + ("..." if len(review.split()) > 12 else "")

def generate_actions(rating, review):
    if rating >= 4:
        return "• Thank customer via email\n• Share feedback with team\n• Request online review/testimonial"
    elif rating == 3:
        return "• Follow up within 24 hours\n• Identify specific concerns\n• Offer discount on next visit"
    else:
        return "• Contact customer immediately\n• Offer full refund or compensation\n• Manager review and staff training"

page = st.sidebar.selectbox("📱 Dashboard", ["User Dashboard", "Admin Dashboard"])

if page == "User Dashboard":
    st.title("⭐ Customer Feedback")
    st.write("Share your experience with us!")
    
    with st.form("feedback_form"):
        col1, col2 = st.columns([1, 3])
        
        with col1:
            rating = st.select_slider("Rating", options=[1, 2, 3, 4, 5], value=5)
            st.write("⭐" * rating)
        
        with col2:
            review = st.text_area("Your Review", placeholder="Tell us about your experience...", height=150)
        
        submitted = st.form_submit_button("✅ Submit", use_container_width=True)
        
        if submitted:
            if review.strip():
                with st.spinner("Processing..."):
                    ai_response = generate_user_response(rating, review)
                    summary = generate_summary(rating, review)
                    actions = generate_actions(rating, review)
                    
                    data = load_data()
                    submission = {
                        'id': len(data) + 1,
                        'timestamp': datetime.now().isoformat(),
                        'rating': rating,
                        'review': review,
                        'ai_response': ai_response,
                        'summary': summary,
                        'actions': actions
                    }
                    data.append(submission)
                    save_data(data)
                    
                    st.success("✅ Thank you!")
                    st.info(f"**Our Response:**\n\n{ai_response}")
            else:
                st.warning("⚠️ Please write a review")
    
    st.divider()
    data = load_data()
    st.caption(f"📊 Total: {len(data)} submissions")

else:
    st.title("🔧 Admin Dashboard")
    
    data = load_data()
    
    if not data:
        st.info("📭 No submissions yet")
    else:
        st.subheader("📊 Analytics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", len(data))
        
        with col2:
            avg = sum(item['rating'] for item in data) / len(data)
            st.metric("Avg", f"{avg:.1f}⭐")
        
        with col3:
            positive = sum(1 for item in data if item['rating'] >= 4)
            st.metric("Positive", f"{positive} ({positive/len(data)*100:.0f}%)")
        
        with col4:
            negative = sum(1 for item in data if item['rating'] <= 2)
            st.metric("Negative", f"{negative} ({negative/len(data)*100:.0f}%)")
        
        st.subheader("📈 Distribution")
        rating_counts = pd.Series([item['rating'] for item in data]).value_counts().sort_index()
        st.bar_chart(rating_counts)
        
        st.subheader("📋 Submissions")
        
        col1, col2 = st.columns(2)
        with col1:
            filter_rating = st.multiselect("Filter", [1,2,3,4,5], [1,2,3,4,5])
        with col2:
            sort_order = st.selectbox("Sort", ["Newest", "Oldest", "Highest", "Lowest"])
        
        filtered = [item for item in data if item['rating'] in filter_rating]
        
        if sort_order == "Newest":
            filtered = sorted(filtered, key=lambda x: x['timestamp'], reverse=True)
        elif sort_order == "Oldest":
            filtered = sorted(filtered, key=lambda x: x['timestamp'])
        elif sort_order == "Highest":
            filtered = sorted(filtered, key=lambda x: x['rating'], reverse=True)
        else:
            filtered = sorted(filtered, key=lambda x: x['rating'])
        
        for item in filtered:
            with st.expander(f"⭐{item['rating']}/5 - #{item['id']} - {item['timestamp'][:10]}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Review:**")
                    st.write(item['review'])
                    st.markdown("**Response:**")
                    st.info(item['ai_response'])
                
                with col2:
                    st.markdown("**Summary:**")
                    st.write(item['summary'])
                    st.markdown("**Actions:**")
                    st.warning(item['actions'])
        
        st.divider()
        if st.button("📥 Export"):
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)
            st.download_button("Download", csv, f"feedback_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")