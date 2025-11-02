from flask import Flask, render_template, request
import pandas as pd
import pywhatkit as kit
import pyautogui
import os
import time
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    report = []
    if request.method == 'POST':
        file = request.files.get('file')

        if not file or not file.filename.endswith('.csv'):
            report.append({'error': 'Please upload a valid CSV file (.csv)'})
            return render_template('index.html', report=report)

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            report.append({'error': f'Error reading CSV file: {e}'})
            return render_template('index.html', report=report)

        required_columns = {'Name', 'Mobile', 'Amount (lacs)'}
        if not required_columns.issubset(df.columns):
            report.append({'error': f'Missing columns. Expected: {", ".join(required_columns)}'})
            return render_template('index.html', report=report)

        for _, row in df.iterrows():
            # Clean up phone (remove .0 if any)
            phone = str(row['Mobile']).strip().split('.')[0]
            name = str(row['Name']).strip()
            #amount = str(row['Amount (lacs)']).strip()

            # ✅ Validate: only 10-digit numbers
            if not phone.isdigit() or len(phone) != 10:
                report.append({'phone': phone, 'name': name, 'status': '⚠️ Skipped: Invalid phone number'})
                continue

            # ✨ WhatsApp message with emojis + contact details
            message = (
                f"👋 Hi {name},\n\n"
                f"Are you looking for fresh funding  or balance transfer of your existing exposure at better pricing ?we’d love to assist you.\n\n"
                "With over 15 years of expertise in financial consulting,"
                "*Coinvest Consulting Endeavors* specializes in simplifying and streamlining finance arrangements for businesses like yours.\n\n"
                "📋 *Our Services include:*\n\n"
                "🏠 A. Home Loan\n"
                "🏢 B. Loan Against Property\n"
                "💰 C. CGTMSE Limit up to ₹10 Cr\n"
                "🚗 D. Car Loan\n"
                "🔁 E. Balance Transfer of Ongoing High-Cost Loans\n"
                "💳 F. Working Capital Limit (CC / OD) up to ₹100 Cr\n"
                "📈 G. Unsecured Business Loans / OD Limits\n"
                "🏫 H. Funding for Schools, Colleges, Hospitals & Nursing Homes\n"
                "    (Including Trusts, Societies & HUFs)\n\n"
                "📞 *Contact:* +91 9354190376\n"
                "✉️ *Email:* coinvestconsultings@gmail.com\n"
                "🌐 *Visit:* www.coinvestconsulting.com\n\n"
                "Let’s connect to discuss the best financing options for your needs.\n\n"
                "— *Team Coinvest Consulting* 🤝"
            )

            try:
                kit.sendwhatmsg_instantly(
                    phone_no=f"+91{phone}",
                    message=message,
                    wait_time=10,
                    tab_close=True
                )
                time.sleep(6)
                pyautogui.hotkey('ctrl', 'w')
                report.append({'phone': phone, 'name': name, 'status': '✅ Sent Successfully'})
            except Exception as e:
                report.append({'phone': phone, 'name': name, 'status': f'❌ Failed: {e}'})

    return render_template('index.html', report=report)


if __name__ == '__main__':
    app.run(debug=True)
