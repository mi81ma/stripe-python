"""
# server_billing.py
Server Billing Management System
This script manages server billing based on uptime and Stripe integration.
"""
import os
import time
import datetime
import psutil
import stripe
from dotenv import load_dotenv
from typing import Dict, Optional
import json

# 環境変数をロード
load_dotenv('.env')  # .envファイルから環境変数を読み込む

class ServerBillingManager:
    def __init__(self):
        """サーバー課金管理クラスの初期化"""
        # Stripe設定
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
        
        # サーバー設定
        self.server_name = os.getenv('SERVER_NAME', 'Unknown Server')
        self.hourly_rate = int(os.getenv('HOURLY_RATE', 100))  # 1時間あたりの料金（円）
        self.currency = os.getenv('CURRENCY', 'jpy')
        
        # サーバー開始時刻を記録
        self.server_start_time = time.time()
        self.boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        
        print(f"🚀 {self.server_name} 課金システム開始")
        print(f"📅 サーバー起動時刻: {self.boot_time}")
        print(f"💰 時間単価: {self.hourly_rate}円/時間")
    
    def get_server_uptime(self) -> Dict:
        """サーバーの稼働時間を取得"""
        current_time = time.time() # 現在のUNIXタイムスタンプを取得
        uptime_seconds = current_time - psutil.boot_time() # サーバーの起動からの経過時間を秒単位で計算
        
        # 時間、分、秒に変換
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        
        return {
            'uptime_seconds': uptime_seconds,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'formatted': f"{hours}時間{minutes}分{seconds}秒"
        }
    
    def calculate_billing_amount(self) -> Dict:
        """稼働時間に基づく課金額を計算"""
        uptime = self.get_server_uptime() # 稼働時間を取得
        
        # 時間単位での課金（最小単位は分）
        total_minutes = uptime['uptime_seconds'] / 60
        billing_hours = total_minutes / 60
        
        # 最小課金時間は1分とする
        if total_minutes < 1:
            billing_amount = self.hourly_rate / 60  # 1分あたりの料金
        else:
            billing_amount = billing_hours * self.hourly_rate
        
        # 円単位に丸める
        billing_amount = round(billing_amount)
        
        return {
            'uptime': uptime,
            'billing_hours': round(billing_hours, 2),
            'billing_amount': billing_amount,
            'currency': self.currency
        }
    
    def create_payment_intent(self, customer_email: Optional[str] = None) -> Dict:
        """Stripe Payment Intentを作成"""
        try:
            billing_info = self.calculate_billing_amount()
            
            # Payment Intent作成
            intent = stripe.PaymentIntent.create(
                amount=billing_info['billing_amount'],
                currency=self.currency,
                metadata={
                    'server_name': self.server_name,
                    'uptime_hours': billing_info['billing_hours'],
                    'uptime_formatted': billing_info['uptime']['formatted'],
                    'start_time': str(self.boot_time),
                    'billing_date': str(datetime.datetime.now())
                }
            )
            
            return {
                'success': True,
                'payment_intent': intent,
                'billing_info': billing_info,
                'client_secret': intent.client_secret
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'billing_info': self.calculate_billing_amount()
            }
    
    def create_test_payment(self) -> Dict:
        """テスト用の決済を実行（サーバーサイドで完結）"""
        try:
            billing_info = self.calculate_billing_amount()
            
            # テスト用のPayment Intentを作成
            intent = stripe.PaymentIntent.create(
                amount=billing_info['billing_amount'],
                currency=self.currency,
                confirm=True,
                payment_method='pm_card_visa',  # Stripeのテスト用PaymentMethod
                metadata={
                    'server_name': self.server_name,
                    'uptime_hours': billing_info['billing_hours'],
                    'uptime_formatted': billing_info['uptime']['formatted'],
                    'start_time': str(self.boot_time),
                    'billing_date': str(datetime.datetime.now()),
                    'test_payment': 'true'
                }
            )
            
            return {
                'success': True,
                'payment_intent': intent,
                'billing_info': billing_info,
                'payment_id': intent.id,
                'status': intent.status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'billing_info': self.calculate_billing_amount()
            }
    
    def create_invoice(self, customer_id: str) -> Dict:
        """定期請求用のインボイスを作成"""
        try:
            billing_info = self.calculate_billing_amount()
            
            # インボイスアイテムを作成
            invoice_item = stripe.InvoiceItem.create(
                customer=customer_id,
                amount=billing_info['billing_amount'],
                currency=self.currency,
                description=f"{self.server_name} サーバー利用料金 ({billing_info['uptime']['formatted']})"
            )
            
            # インボイスを作成
            invoice = stripe.Invoice.create(
                customer=customer_id,
                metadata={
                    'server_name': self.server_name,
                    'uptime_hours': billing_info['billing_hours'],
                    'billing_period': f"{self.boot_time} - {datetime.datetime.now()}"
                }
            )
            
            return {
                'success': True,
                'invoice': invoice,
                'invoice_item': invoice_item,
                'billing_info': billing_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_billing_summary(self) -> Dict:
        """課金サマリーを取得"""
        billing_info = self.calculate_billing_amount()
        
        return {
            'server_name': self.server_name,
            'boot_time': str(self.boot_time),
            'current_time': str(datetime.datetime.now()),
            'uptime': billing_info['uptime']['formatted'],
            'hourly_rate': self.hourly_rate,
            'total_amount': billing_info['billing_amount'],
            'currency': self.currency
        }
    
    def print_billing_status(self):
        """現在の課金状況を表示"""
        summary = self.get_billing_summary()
        
        print("\n" + "="*50)
        print(f"📊 {summary['server_name']} 課金状況")
        print("="*50)
        print(f"🕐 起動時刻: {summary['boot_time']}")
        print(f"⏱️  稼働時間: {summary['uptime']}")
        print(f"💰 時間単価: {summary['hourly_rate']}円/時間")
        print(f"💸 現在の課金額: {summary['total_amount']}円")
        print("="*50)

# 使用例
if __name__ == "__main__":
    # 課金管理システムを初期化
    billing_manager = ServerBillingManager()
    
    # 現在の課金状況を表示
    billing_manager.print_billing_status()
    
    # Payment Intentを作成（即座決済用）
    payment_result = billing_manager.create_payment_intent()
    
    if payment_result['success']:
        print(f"\n✅ Payment Intent作成成功")
        print(f"Client Secret: {payment_result['client_secret']}")
        print(f"課金額: {payment_result['billing_info']['billing_amount']}円")
    else:
        print(f"\n❌ Payment Intent作成失敗: {payment_result['error']}")
    
    # 課金サマリーをJSONで出力
    summary = billing_manager.get_billing_summary()
    print(f"\n📋 課金サマリー (JSON):")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
