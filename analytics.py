import streamlit as st
import pymysql
import pandas as pd
import os
import io
from datetime import datetime, timedelta
from itertools import combinations
from collections import defaultdict

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

st.set_page_config(page_title="Food Court Analytics", page_icon="🍽️", layout="wide")

@st.cache_resource
def get_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'foodcourt_db'),
        cursorclass=pymysql.cursors.DictCursor
    )

def run_query(sql):
    try:
        conn = get_connection()
        conn.ping(reconnect=True)
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return pd.DataFrame(cursor.fetchall())
    except Exception as e:
        st.error(f"DB Error: {e}")
        return pd.DataFrame()

st.sidebar.title("🍽️ Food Court Analytics")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", [
    "📊 Overview",
    "🎯 Customer Segmentation",
    "🏪 Vendor Scorecard",
    "📋 Recent Orders",
    "🤖 Food Recommendations",
    "📄 Reports"
])
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_resource.clear()
    st.rerun()

orders_df  = run_query("SELECT * FROM orders WHERE status != 'cancelled'")
items_df   = run_query("SELECT oi.*, mi.name as item_name, v.name as vendor_name FROM order_items oi JOIN menu_items mi ON oi.item_id = mi.item_id JOIN vendors v ON oi.vendor_id = v.vendor_id")
users_df   = run_query("SELECT * FROM users WHERE role = 'customer'")
vendors_df = run_query("SELECT * FROM vendors")
menu_df    = run_query("SELECT * FROM menu_items")

# ── OVERVIEW ──────────────────────────────────────────────
if page == "📊 Overview":
    st.title("📊 Food Court Overview")
    st.markdown("---")
    total_revenue = float(orders_df['total'].sum()) if not orders_df.empty else 0
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("💰 Total Revenue", f"₹{total_revenue:,.0f}")
    with col2: st.metric("📦 Total Orders", len(orders_df))
    with col3: st.metric("👥 Customers", len(users_df))
    with col4: st.metric("🏪 Vendors", len(vendors_df))
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Orders by Status")
        if not orders_df.empty:
            s = orders_df['status'].value_counts().reset_index()
            s.columns = ['Status', 'Count']
            st.bar_chart(s.set_index('Status'))
        else:
            st.info("No orders yet")
    with col2:
        st.subheader("🏪 Revenue by Vendor")
        if not items_df.empty:
            v = items_df.copy()
            v['revenue'] = v['unit_price'].astype(float) * v['quantity']
            v = v.groupby('vendor_name')['revenue'].sum().reset_index()
            v.columns = ['Vendor', 'Revenue']
            st.bar_chart(v.set_index('Vendor'))
        else:
            st.info("No revenue data yet")
    st.markdown("---")
    st.subheader("🔥 Top Selling Items")
    if not items_df.empty:
        top = items_df.groupby('item_name').agg(Sold=('quantity','sum')).sort_values('Sold', ascending=False).head(8).reset_index()
        top.columns = ['Item', 'Sold']
        st.dataframe(top, use_container_width=True, hide_index=True)
    else:
        st.info("No sales data yet")

# ── CUSTOMER SEGMENTATION ─────────────────────────────────
elif page == "🎯 Customer Segmentation":
    st.title("🎯 Customer Segmentation")
    st.markdown("Automatically categorizes customers based on spending and order behavior.")
    st.markdown("---")
    if orders_df.empty or users_df.empty:
        st.info("No customer data yet. Place some orders first!")
    else:
        customer_stats = run_query("""
            SELECT u.user_id, u.name as Customer, u.email as Email,
                   COUNT(o.order_id) as total_orders,
                   COALESCE(SUM(o.total), 0) as total_spent,
                   MAX(o.created_at) as last_order
            FROM users u
            LEFT JOIN orders o ON u.user_id = o.user_id AND o.status != 'cancelled'
            WHERE u.role = 'customer'
            GROUP BY u.user_id, u.name, u.email
        """)
        if not customer_stats.empty:
            customer_stats['total_spent'] = customer_stats['total_spent'].astype(float)
            customer_stats['total_orders'] = customer_stats['total_orders'].astype(int)
            customer_stats['last_order'] = pd.to_datetime(customer_stats['last_order'])
            now = datetime.now()
            def segment(row):
                days_since = (now - row['last_order']).days if pd.notnull(row['last_order']) else 999
                if row['total_spent'] >= 1000: return '🐋 Whale'
                elif row['total_orders'] >= 3: return '🔄 Regular'
                elif days_since > 7: return '😴 Inactive'
                elif row['total_orders'] >= 1: return '🆕 New'
                else: return '👋 Visitor'
            customer_stats['Segment'] = customer_stats.apply(segment, axis=1)
            segments = customer_stats['Segment'].value_counts()
            st.subheader("Segment Summary")
            cols = st.columns(len(segments))
            for i, (seg, count) in enumerate(segments.items()):
                with cols[i]:
                    avg = customer_stats[customer_stats['Segment']==seg]['total_spent'].mean()
                    st.metric(seg, f"{count} customers", f"Avg ₹{avg:,.0f}")
            st.markdown("---")
            selected_seg = st.selectbox("Filter by Segment", ['All'] + list(segments.index))
            filtered = customer_stats if selected_seg == 'All' else customer_stats[customer_stats['Segment']==selected_seg]
            display = filtered[['Customer','Email','total_orders','total_spent','Segment']].copy()
            display.columns = ['Customer','Email','Orders','Total Spent','Segment']
            display['Total Spent'] = display['Total Spent'].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(display, use_container_width=True, hide_index=True)
            st.markdown("---")
            st.subheader("📊 Spending by Segment")
            st.bar_chart(customer_stats.groupby('Segment')['total_spent'].sum())

# ── VENDOR SCORECARD ──────────────────────────────────────
elif page == "🏪 Vendor Scorecard":
    st.title("🏪 Vendor Scorecard")
    st.markdown("Performance rating for each vendor based on orders, revenue and completion rate.")
    st.markdown("---")
    vendor_scores = run_query("""
        SELECT v.name as Vendor, v.emoji as Emoji,
               COUNT(DISTINCT o.order_id) as total_orders,
               COALESCE(SUM(oi.unit_price * oi.quantity), 0) as total_revenue,
               SUM(CASE WHEN oi.item_status = 'collected' THEN 1 ELSE 0 END) as completed_items,
               COUNT(oi.order_item_id) as total_items,
               COUNT(DISTINCT mi.item_id) as menu_size
        FROM vendors v
        LEFT JOIN order_items oi ON v.vendor_id = oi.vendor_id
        LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status != 'cancelled'
        LEFT JOIN menu_items mi ON v.vendor_id = mi.vendor_id
        GROUP BY v.vendor_id, v.name, v.emoji
    """)
    if not vendor_scores.empty:
        vendor_scores['total_revenue'] = vendor_scores['total_revenue'].astype(float)
        vendor_scores['total_orders'] = vendor_scores['total_orders'].astype(int)
        vendor_scores['completed_items'] = vendor_scores['completed_items'].astype(int)
        vendor_scores['total_items'] = vendor_scores['total_items'].astype(int)
        max_rev = vendor_scores['total_revenue'].max() or 1
        max_ord = vendor_scores['total_orders'].max() or 1
        def calc_score(row):
            r = (row['total_revenue']/max_rev)*40
            o = (row['total_orders']/max_ord)*30
            c = (row['completed_items']/row['total_items']*100/100)*30 if row['total_items'] > 0 else 0
            return round(r+o+c, 1)
        vendor_scores['Score'] = vendor_scores.apply(calc_score, axis=1)
        vendor_scores['Completion'] = vendor_scores.apply(lambda r: round(r['completed_items']/r['total_items']*100,1) if r['total_items']>0 else 0, axis=1)
        def grade(s):
            if s>=80: return '🥇 Excellent'
            elif s>=60: return '🥈 Good'
            elif s>=40: return '🥉 Average'
            else: return '📉 Needs Improvement'
        vendor_scores['Grade'] = vendor_scores['Score'].apply(grade)
        vendor_scores = vendor_scores.sort_values('Score', ascending=False)
        for _, row in vendor_scores.iterrows():
            c1,c2,c3,c4,c5 = st.columns([2,2,2,2,2])
            with c1:
                st.markdown(f"### {row['Emoji']} {row['Vendor']}")
                st.markdown(f"**{row['Grade']}**")
            with c2: st.metric("📦 Orders", row['total_orders'])
            with c3: st.metric("💰 Revenue", f"₹{row['total_revenue']:,.0f}")
            with c4: st.metric("✅ Completion", f"{row['Completion']}%")
            with c5: st.metric("⭐ Score", f"{row['Score']}/100")
            st.progress(float(row['Score'])/100)
            st.markdown("---")
        st.subheader("📊 Score Comparison")
        st.bar_chart(vendor_scores.set_index('Vendor')['Score'])
    else:
        st.info("No vendor data yet!")

# ── RECENT ORDERS ─────────────────────────────────────────
elif page == "📋 Recent Orders":
    st.title("📋 Recent Orders")
    st.markdown("---")
    recent = run_query("""
        SELECT o.token_number as Token, u.name as Customer,
               o.total as Total, o.status as Status, o.created_at as Time
        FROM orders o JOIN users u ON o.user_id = u.user_id
        ORDER BY o.created_at DESC LIMIT 50
    """)
    if not recent.empty:
        sf = st.multiselect("Filter by Status", recent['Status'].unique().tolist(), default=recent['Status'].unique().tolist())
        filtered = recent[recent['Status'].isin(sf)]
        filtered['Total'] = filtered['Total'].apply(lambda x: f"₹{float(x):,.0f}")
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.caption(f"Showing {len(filtered)} orders")
    else:
        st.info("No orders yet!")

# ── FOOD RECOMMENDATIONS ──────────────────────────────────
elif page == "🤖 Food Recommendations":
    st.title("🤖 Food Recommendation Engine")
    st.markdown("Uses **Market Basket Analysis** — finds items frequently ordered together.")
    st.markdown("---")
    order_items = run_query("""
        SELECT o.order_id, mi.name as item_name
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN menu_items mi ON oi.item_id = mi.item_id
        WHERE o.status != 'cancelled'
    """)
    if order_items.empty or len(order_items) < 2:
        st.info("Not enough order data yet. Need at least a few orders to generate recommendations!")
    else:
        orders_grouped = order_items.groupby('order_id')['item_name'].apply(list)
        pair_counts = defaultdict(int)
        item_counts = defaultdict(int)
        for items_list in orders_grouped:
            unique_items = list(set(items_list))
            for item in unique_items:
                item_counts[item] += 1
            for pair in combinations(sorted(unique_items), 2):
                pair_counts[pair] += 1
        recommendations = []
        for (item_a, item_b), count in pair_counts.items():
            if count >= 1:
                conf_ab = count / item_counts[item_a] * 100
                conf_ba = count / item_counts[item_b] * 100
                recommendations.append({'If customer orders': item_a, 'Recommend': item_b, 'Ordered Together': count, 'Confidence': f"{conf_ab:.0f}%"})
                recommendations.append({'If customer orders': item_b, 'Recommend': item_a, 'Ordered Together': count, 'Confidence': f"{conf_ba:.0f}%"})
        if recommendations:
            rec_df = pd.DataFrame(recommendations).sort_values('Ordered Together', ascending=False)
            st.subheader("🔍 Find Recommendations")
            all_items = sorted(order_items['item_name'].unique().tolist())
            selected_item = st.selectbox("Select an item:", all_items)
            filtered_rec = rec_df[rec_df['If customer orders'] == selected_item]
            if not filtered_rec.empty:
                st.success(f"Customers who ordered **{selected_item}** also ordered:")
                for _, row in filtered_rec.iterrows():
                    c1,c2,c3 = st.columns([3,2,2])
                    with c1: st.markdown(f"🍽️ **{row['Recommend']}**")
                    with c2: st.markdown(f"Together: **{row['Ordered Together']}x**")
                    with c3: st.markdown(f"Confidence: **{row['Confidence']}**")
            else:
                st.info(f"No co-order data for {selected_item} yet.")
            st.markdown("---")
            st.subheader("🏆 Most Popular Combinations")
            seen = set()
            top_pairs = []
            for (a,b), count in sorted(pair_counts.items(), key=lambda x: -x[1]):
                key = tuple(sorted([a,b]))
                if key not in seen:
                    seen.add(key)
                    top_pairs.append({'Item A': a, 'Item B': b, 'Times Ordered Together': count})
            st.dataframe(pd.DataFrame(top_pairs).head(10), use_container_width=True, hide_index=True)
        else:
            st.info("Need more orders with multiple items!")

# ── REPORTS ───────────────────────────────────────────────
elif page == "📄 Reports":
    st.title("📄 Reports")
    st.markdown("Download reports as Excel or PDF.")
    st.markdown("---")
    report_type = st.radio("Report Type", ["📦 Orders","💰 Revenue","🏪 Vendor Performance","👥 Customers"])
    c1,c2 = st.columns(2)
    with c1: start_date = st.date_input("From", datetime.now()-timedelta(days=30))
    with c2: end_date = st.date_input("To", datetime.now())
    st.markdown("---")
    if report_type == "📦 Orders":
        df = run_query(f"SELECT o.token_number as Token, u.name as Customer, o.total as Total, o.status as Status, o.created_at as Time FROM orders o JOIN users u ON o.user_id=u.user_id WHERE DATE(o.created_at) BETWEEN '{start_date}' AND '{end_date}' ORDER BY o.created_at DESC")
        title = "Orders_Report"
    elif report_type == "💰 Revenue":
        df = run_query(f"SELECT v.name as Vendor, COUNT(DISTINCT o.order_id) as Orders, SUM(oi.unit_price*oi.quantity) as Revenue FROM order_items oi JOIN orders o ON oi.order_id=o.order_id JOIN vendors v ON oi.vendor_id=v.vendor_id WHERE DATE(o.created_at) BETWEEN '{start_date}' AND '{end_date}' AND o.status!='cancelled' GROUP BY v.name ORDER BY Revenue DESC")
        title = "Revenue_Report"
    elif report_type == "🏪 Vendor Performance":
        df = run_query(f"SELECT v.name as Vendor, COUNT(DISTINCT o.order_id) as Orders, SUM(oi.unit_price*oi.quantity) as Revenue, SUM(CASE WHEN oi.item_status='collected' THEN 1 ELSE 0 END) as Completed FROM vendors v LEFT JOIN order_items oi ON v.vendor_id=oi.vendor_id LEFT JOIN orders o ON oi.order_id=o.order_id WHERE DATE(o.created_at) BETWEEN '{start_date}' AND '{end_date}' GROUP BY v.name")
        title = "Vendor_Performance_Report"
    else:
        df = run_query("SELECT u.name as Customer, u.email as Email, COUNT(o.order_id) as Orders, SUM(o.total) as Total_Spent FROM users u LEFT JOIN orders o ON u.user_id=o.user_id WHERE u.role='customer' GROUP BY u.user_id,u.name,u.email ORDER BY Total_Spent DESC")
        title = "Customer_Report"
    if not df.empty:
        st.subheader(f"Preview — {title}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(df)} records")
        c1,c2 = st.columns(2)
        with c1:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                df.to_excel(w, index=False, sheet_name=title)
            st.download_button("📥 Download Excel", buf.getvalue(), f"{title}_{start_date}_{end_date}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with c2:
            if PDF_AVAILABLE:
                pdf_buf = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buf, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = [
                    Paragraph(f"Food Court — {title.replace('_',' ')}", styles['Title']),
                    Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']),
                    Spacer(1,12)
                ]
                tdata = [df.columns.tolist()] + df.astype(str).values.tolist()
                t = Table(tdata, repeatRows=1)
                t.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1a1a2e')),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                    ('FONTSIZE',(0,0),(-1,-1),8),
                    ('GRID',(0,0),(-1,-1),0.5,colors.grey),
                    ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f5f5f5')]),
                ]))
                elements.append(t)
                doc.build(elements)
                st.download_button("📥 Download PDF", pdf_buf.getvalue(), f"{title}_{start_date}_{end_date}.pdf", "application/pdf")
            else:
                st.warning("Install reportlab for PDF: pip install reportlab")
    else:
        st.info("No data for selected date range!")
