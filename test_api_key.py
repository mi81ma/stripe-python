#!/usr/bin/env python3
"""
Stripe APIキーの読み込みテスト
"""

import os
from dotenv import load_dotenv
import stripe

# 環境変数をロード
load_dotenv('.env')

def test_api_key():
    """APIキーの読み込みと有効性をテスト"""
    
    print("🔍 環境変数の確認...")
    
    # 環境変数の確認
    secret_key = os.getenv('STRIPE_SECRET_KEY')
    publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')
    
    print(f"STRIPE_SECRET_KEY: {secret_key[:15] + '...' if secret_key else 'None'}")
    print(f"STRIPE_PUBLISHABLE_KEY: {publishable_key[:15] + '...' if publishable_key else 'None'}")
    
    if not secret_key:
        print("❌ STRIPE_SECRET_KEYが読み込まれていません")
        return False
    
    if not publishable_key:
        print("❌ STRIPE_PUBLISHABLE_KEYが読み込まれていません")
        return False
    
    # Stripeライブラリに設定
    stripe.api_key = secret_key
    
    print("\n🧪 Stripe API接続テスト...")
    
    try:
        # APIキーの有効性をテスト（アカウント情報を取得）
        account = stripe.Account.retrieve()
        print(f"✅ API接続成功!")
        print(f"アカウントID: {account.id}")
        print(f"アカウント名: {account.business_profile.name if account.business_profile else 'N/A'}")
        print(f"国: {account.country}")
        print(f"通貨: {account.default_currency}")
        
        return True
        
    except stripe.error.AuthenticationError as e:
        print(f"❌ 認証エラー: {e}")
        print("APIキーが無効です")
        return False
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripeエラー: {e}")
        return False
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def test_payment_intent_creation():
    """Payment Intent作成のテスト"""
    
    print("\n💳 Payment Intent作成テスト...")
    
    try:
        # テスト用のPayment Intentを作成
        intent = stripe.PaymentIntent.create(
            amount=100,  # 100円
            currency='jpy',
            metadata={
                'test': 'api_key_validation'
            }
        )
        
        print(f"✅ Payment Intent作成成功!")
        print(f"Payment Intent ID: {intent.id}")
        print(f"Status: {intent.status}")
        print(f"Amount: {intent.amount}円")
        
        return True
        
    except stripe.error.AuthenticationError as e:
        print(f"❌ 認証エラー: {e}")
        return False
        
    except stripe.error.StripeError as e:
        print(f"❌ Stripeエラー: {e}")
        return False
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Stripe APIキー検証ツール")
    print("=" * 50)
    
    # APIキーのテスト
    if test_api_key():
        # Payment Intent作成のテスト
        test_payment_intent_creation()
    
    print("\n" + "=" * 50)
    print("テスト完了")
