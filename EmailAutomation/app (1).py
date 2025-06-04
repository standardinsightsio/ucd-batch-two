from flask import Flask, request, render_template
from flask_apscheduler import APScheduler
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime

app = Flask(__name__)

class Config:
    SCHEDULER_API_ENABLED = True

app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# Helper function to send email
def send_email(subject, body_html, sender_email, sender_password, receiver_emails):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_emails)
    msg.attach(MIMEText(body_html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_emails, msg.as_string())

# Render appropriate report
def render_report(report_type):
    return render_template(f"{report_type}_report_template.html")

@app.route("/", methods=["GET"])
def index():
    return render_template("config.html")

@app.route("/preview", methods=["POST"])
def preview():
    sender_email = request.form["sender_email"]
    sender_password = request.form["sender_password"]
    receiver_email = [email.strip() for email in request.form["receiver_email"].split(",")]
    report_type = request.form["report_type"]
    custom_message = request.form["custom_message"]
    send_time = request.form.get("send_time", "08:00")  # HH:MM
    send_mode = request.form.get("send_mode", "fixed")  # fixed or custom
    send_dates = request.form.get("send_dates", "")     # for custom mode

    hour, minute = map(int, send_time.split(":"))

    def job_func():
        report_html = render_report(report_type)
        full_html = f"<p>{custom_message}</p>{report_html}"
        send_email("Your Scheduled Business Report", full_html, sender_email, sender_password, receiver_email)

    if send_mode == "fixed":
        # daily at specified time
        job_id = f"fixed_{datetime.datetime.now().timestamp()}"
        scheduler.add_job(id=job_id, func=job_func, trigger="cron", hour=hour, minute=minute)
    else:
        # for multiple one-time specific dates
        for date_str in send_dates.split(","):
            date_str = date_str.strip()
            try:
                send_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                scheduled_dt = send_date.replace(hour=hour, minute=minute, second=0)
                job_id = f"custom_{scheduled_dt.strftime('%Y%m%d%H%M')}_{datetime.datetime.now().timestamp()}"
                scheduler.add_job(id=job_id, func=job_func, trigger="date", run_date=scheduled_dt)
            except ValueError:
                return f"Invalid date format: {date_str}. Please use YYYY-MM-DD."

    return f"Scheduled report ({report_type}) successfully."

if __name__ == "__main__":
    app.run(debug=True)