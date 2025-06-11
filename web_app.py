from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from server_billing import ServerBillingManager

app = FastAPI(title="Server Billing System", version="1.0.0")

# Initialize billing management system
billing_manager = ServerBillingManager()

@app.get("/", response_class=HTMLResponse)
async def index():
    """Main page"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Server Billing System</title>
        <script src="https://js.stripe.com/v3/"></script>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }}
            .billing-info {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                border-left: 4px solid #007bff;
            }}
            .status {{
                margin: 20px 0;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }}
            .button {{
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px 5px;
                transition: background-color 0.3s;
            }}
            .button:hover {{
                background: #0056b3;
            }}
            #payment-form {{
                display: none;
                margin-top: 20px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background: #f9f9f9;
            }}
            #card-element {{
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 10px;
                margin: 15px 0;
            }}
            .update-info {{
                text-align: center;
                color: #666;
                font-size: 14px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Server Billing System</h1>
                <p>Automatic billing based on uptime</p>
            </div>
            
            <div id="billing-info" class="billing-info">
                <h3>📊 Current Billing Status</h3>
                <div id="server-info">
                    <p><strong>Server Name:</strong> <span id="server-name">Loading...</span></p>
                    <p><strong>Uptime:</strong> <span id="uptime">Loading...</span></p>
                    <p><strong>Hourly Rate:</strong> <span id="hourly-rate">Loading...</span></p>
                    <p><strong>Current Billing Amount:</strong> <span id="billing-amount">Loading...</span></p>
                </div>
            </div>
            
            <div id="payment-status" class="status"></div>
            
            <div style="text-align: center;">
                <button onclick="createPayment()" class="button">💳 Start Payment</button>
                <button onclick="updateBillingInfo()" class="button">🔄 Update Info</button>
            </div>
            
            <div id="payment-form">
                <h3>💳 Enter Card Information</h3>
                <div id="card-element"></div>
                <button onclick="confirmPayment()" class="button">Execute Payment</button>
                <button onclick="cancelPayment()" class="button" style="background: #dc3545;">Cancel</button>
            </div>
            
            <div class="update-info">
                <p>💡 Information is automatically updated every 30 seconds</p>
            </div>
        </div>

        <script>
            const stripe = Stripe('{billing_manager.publishable_key}');
            let cardElement;
            let clientSecret;

            async function setupStripeElements() {{
                const elements = stripe.elements();
                cardElement = elements.create('card', {{
                    style: {{
                        base: {{
                            fontSize: '16px',
                            color: '#424770',
                            '::placeholder': {{
                                color: '#aab7c4',
                            }},
                        }},
                    }},
                }});
                cardElement.mount('#card-element');
            }}

            async function createPayment() {{
                try {{
                    // Create Payment Intent
                    const response = await fetch('/api/create-payment-intent', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }}
                    }});
                    
                    const data = await response.json();
                    
                    if (data.success) {{
                        clientSecret = data.client_secret;
                        
                        // Show card input form
                        document.getElementById('payment-form').style.display = 'block';
                        document.getElementById('payment-status').innerHTML = `💳 Please enter card information to complete payment (Billing amount: ${{data.billing_info.billing_amount}} yen)`;
                        document.getElementById('payment-status').style.background = '#d4edda';
                        document.getElementById('payment-status').style.color = '#155724';
                        
                        // Setup Stripe Elements
                        await setupStripeElements();
                        
                    }} else {{
                        document.getElementById('payment-status').innerHTML = `❌ Payment setup error: ${{data.error}}`;
                        document.getElementById('payment-status').style.background = '#f8d7da';
                        document.getElementById('payment-status').style.color = '#721c24';
                    }}
                }} catch (error) {{
                    console.error('Error:', error);
                    document.getElementById('payment-status').innerHTML = '❌ Payment processing failed';
                    document.getElementById('payment-status').style.background = '#f8d7da';
                    document.getElementById('payment-status').style.color = '#721c24';
                }}
            }}

            async function confirmPayment() {{
                if (!clientSecret || !cardElement) {{
                    document.getElementById('payment-status').innerHTML = '❌ Payment is not ready';
                    document.getElementById('payment-status').style.background = '#f8d7da';
                    document.getElementById('payment-status').style.color = '#721c24';
                    return;
                }}

                const {{ error, paymentIntent }} = await stripe.confirmCardPayment(clientSecret, {{
                    payment_method: {{
                        card: cardElement,
                    }}
                }});

                if (error) {{
                    document.getElementById('payment-status').innerHTML = `❌ Payment error: ${{error.message}}`;
                    document.getElementById('payment-status').style.background = '#f8d7da';
                    document.getElementById('payment-status').style.color = '#721c24';
                }} else {{
                    document.getElementById('payment-status').innerHTML = `✅ Payment completed! Payment ID: ${{paymentIntent.id}}`;
                    document.getElementById('payment-status').style.background = '#d4edda';
                    document.getElementById('payment-status').style.color = '#155724';
                    document.getElementById('payment-form').style.display = 'none';
                    updateBillingInfo(); // Update information after payment
                }}
            }}

            function cancelPayment() {{
                document.getElementById('payment-form').style.display = 'none';
                document.getElementById('payment-status').innerHTML = '❌ Payment was cancelled';
                document.getElementById('payment-status').style.background = '#f8d7da';
                document.getElementById('payment-status').style.color = '#721c24';
            }}

            async function updateBillingInfo() {{
                try {{
                    const response = await fetch('/api/billing-status');
                    const data = await response.json();
                    
                    document.getElementById('server-name').textContent = data.server_name;
                    document.getElementById('uptime').textContent = data.uptime;
                    document.getElementById('hourly-rate').textContent = `${{data.hourly_rate}} yen/hour`;
                    document.getElementById('billing-amount').textContent = `${{data.total_amount}} yen`;
                }} catch (error) {{
                    console.error('Error updating billing info:', error);
                }}
            }}

            // Get billing information on initialization
            updateBillingInfo();
            
            // Auto-update every 30 seconds
            setInterval(updateBillingInfo, 30000);
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/create-payment-intent")
async def create_payment_intent():
    """Create Payment Intent"""
    result = billing_manager.create_payment_intent()
    return JSONResponse(content=result)

@app.get("/api/billing-status")
async def get_billing_status():
    """Get current billing status"""
    return JSONResponse(content=billing_manager.get_billing_summary())

@app.get("/api/uptime")
async def get_uptime():
    """Get server uptime"""
    return JSONResponse(content=billing_manager.get_server_uptime())

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    print(f"🌐 Starting Server Billing System...")
    print(f"📍 URL: http://localhost:{port}")
    print(f"💡 Access with browser to test payments")
    
    uvicorn.run("web_app:app", host="0.0.0.0", port=port, reload=True)
