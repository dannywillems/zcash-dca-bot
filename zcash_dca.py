#!/usr/bin/env python3
"""
ZCash DCA Bot - Automated daily purchases on Kraken with social media updates

This bot performs Dollar Cost Averaging (DCA) purchases of ZCash on Kraken.
It tracks accumulation and generates social media updates.

Author: Your Name
License: MIT
Repository: https://github.com/yourusername/zcash-dca-bot
"""

import os
import json
from pathlib import Path
from datetime import datetime
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from typing import Dict, List, Optional
import ccxt
import fire
from dotenv import load_dotenv


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal objects."""
    
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class PurchaseRecord:
    """Represents a single ZCash purchase."""
    
    def __init__(
        self,
        date: str,
        zec_bought: Decimal,
        eur_spent: Decimal,
        price_per_zec: Decimal,
        order_id: Optional[str] = None,
        dry_run: bool = False
    ):
        self.date = date
        self.zec_bought = Decimal(str(zec_bought))
        self.eur_spent = Decimal(str(eur_spent))
        self.price_per_zec = Decimal(str(price_per_zec))
        self.order_id = order_id
        self.dry_run = dry_run
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'date': self.date,
            'zec_bought': str(self.zec_bought),
            'eur_spent': str(self.eur_spent),
            'price_per_zec': str(self.price_per_zec),
            'order_id': self.order_id,
            'dry_run': self.dry_run
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PurchaseRecord':
        """Create PurchaseRecord from dictionary."""
        return cls(
            date=data['date'],
            zec_bought=Decimal(data['zec_bought']),
            eur_spent=Decimal(data['eur_spent']),
            price_per_zec=Decimal(data['price_per_zec']),
            order_id=data.get('order_id'),
            dry_run=data.get('dry_run', False)
        )


class AccumulationTracker:
    """Tracks accumulated ZCash purchases over time."""
    
    def __init__(self, tracking_file: Path):
        self.tracking_file = tracking_file
        self.total_zec = Decimal('0')
        self.total_eur_spent = Decimal('0')
        self.purchases: List[PurchaseRecord] = []
        self.load_data()
    
    def load_data(self) -> None:
        """Load accumulated data from JSON file."""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                
                self.total_zec = Decimal(data.get('total_zec', '0'))
                self.total_eur_spent = Decimal(data.get('total_eur_spent', '0'))
                
                self.purchases = [
                    PurchaseRecord.from_dict(p)
                    for p in data.get('purchases', [])
                ]
                
                print(f"✓ Loaded {len(self.purchases)} previous purchases")
                
            except (json.JSONDecodeError, KeyError, InvalidOperation) as e:
                print(f"⚠️  Warning: Could not load tracking file: {e}")
                print("Starting with fresh tracking data")
                self._initialize_empty_data()
        else:
            print("ℹ️  No previous tracking file found, starting fresh")
            self._initialize_empty_data()
    
    def _initialize_empty_data(self) -> None:
        """Initialize empty tracking data."""
        self.total_zec = Decimal('0')
        self.total_eur_spent = Decimal('0')
        self.purchases = []
    
    def add_purchase(self, purchase: PurchaseRecord) -> None:
        """Add a new purchase and update totals."""
        self.purchases.append(purchase)
        self.total_zec += purchase.zec_bought
        self.total_eur_spent += purchase.eur_spent
        self.save_data()
    
    def save_data(self) -> None:
        """Save tracking data to JSON file."""
        data = {
            'total_zec': str(self.total_zec),
            'total_eur_spent': str(self.total_eur_spent),
            'purchases': [p.to_dict() for p in self.purchases]
        }
        
        with open(self.tracking_file, 'w') as f:
            json.dump(data, f, indent=2, cls=DecimalEncoder)
    
    def get_average_price(self) -> Optional[Decimal]:
        """Calculate average price per ZEC."""
        if self.total_zec > 0:
            return (self.total_eur_spent / self.total_zec).quantize(
                Decimal('0.01'), rounding=ROUND_DOWN
            )
        return None
    
    def get_stats(self) -> Dict:
        """Get accumulation statistics."""
        return {
            'total_zec': self.total_zec,
            'total_eur_spent': self.total_eur_spent,
            'average_price': self.get_average_price(),
            'num_purchases': len(self.purchases),
            'first_purchase': self.purchases[0].date if self.purchases else None,
            'last_purchase': self.purchases[-1].date if self.purchases else None
        }


class KrakenClient:
    """Wrapper for Kraken exchange operations."""
    
    def __init__(self, api_key: str, secret_key: str):
        self.exchange = ccxt.kraken({
            'apiKey': api_key,
            'secret': secret_key,
            'enableRateLimit': True,
        })
        self.symbol = 'ZEC/EUR'
    
    def get_current_price(self) -> Decimal:
        """Fetch current ZEC/EUR price from Kraken."""
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            price = Decimal(str(ticker['last']))
            return price.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        except Exception as e:
            raise Exception(f"Failed to fetch price from Kraken: {e}")
    
    def calculate_zec_amount(self, eur_amount: Decimal, price: Decimal) -> Decimal:
        """Calculate how much ZEC can be bought with given EUR amount."""
        zec_amount = eur_amount / price
        # Round to 8 decimal places (common for cryptocurrencies)
        return zec_amount.quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
    
    def execute_market_buy(self, zec_amount: Decimal) -> Dict:
        """Execute market buy order on Kraken."""
        try:
            # Convert Decimal to float for CCXT
            order = self.exchange.create_market_buy_order(
                self.symbol,
                float(zec_amount)
            )
            return order
        except Exception as e:
            raise Exception(f"Failed to execute order on Kraken: {e}")


class SocialMediaPoster:
    """Handles social media post generation and posting."""
    
    @staticmethod
    def generate_post(
        purchase: PurchaseRecord,
        total_zec: Decimal
    ) -> str:
        """
        Generate social media post text.
        
        Args:
            purchase: Purchase record
            total_zec: Total accumulated ZEC
        
        Returns:
            Formatted social media post
        """
        date_obj = datetime.fromisoformat(purchase.date)
        date_str = date_obj.strftime('%B %d, %Y')
        
        # Format decimals for display
        zec_bought = purchase.zec_bought.quantize(Decimal('0.00000001'))
        eur_spent = purchase.eur_spent.quantize(Decimal('0.01'))
        price = purchase.price_per_zec.quantize(Decimal('0.01'))
        total = total_zec.quantize(Decimal('0.00000001'))
        
        post = f"""🪙 Daily #ZCash DCA Update - {date_str}

📊 Today's Purchase:
• Bought: {zec_bought} ZEC
• Spent: €{eur_spent}
• Price: €{price} per ZEC

💎 Total Accumulated: {total} ZEC

#Zcash #Crypto #DCA #DollarCostAveraging"""
        
        if purchase.dry_run:
            post = "🔍 DRY RUN - " + post
        
        return post
    
    @staticmethod
    def display_post(text: str) -> None:
        """Display the post to console."""
        print("\n📱 Social Media Post:")
        print("=" * 70)
        print(text)
        print("=" * 70)
        print("\n💡 Copy the text above to post manually on your social platforms")
        print("   or implement API integration in the post_to_platforms() method.")


class ZCashDCABot:
    """Main bot for automated ZCash DCA purchases."""
    
    def __init__(self):
        """Initialize the bot with configuration and dependencies."""
        load_dotenv()
        
        # Validate required environment variables
        self.api_key = os.getenv('KRAKEN_API_KEY')
        self.secret_key = os.getenv('KRAKEN_SECRET_KEY')
        
        if not self.api_key or not self.secret_key:
            raise ValueError(
                "Missing Kraken credentials! "
                "Please set KRAKEN_API_KEY and KRAKEN_SECRET_KEY in .env file"
            )
        
        # Initialize components
        self.kraken = KrakenClient(self.api_key, self.secret_key)
        self.tracker = AccumulationTracker(Path('zcash_accumulation.json'))
        self.social = SocialMediaPoster()
    
    def buy(
        self,
        amount_eur: float,
        dry_run: bool = False,
        post: bool = True
    ) -> Dict:
        """
        Execute a ZCash purchase.
        
        Args:
            amount_eur: Amount in EUR to spend on ZCash
            dry_run: If True, simulate without actually buying
            post: If True, generate social media post
        
        Returns:
            Dictionary with purchase details
        """
        try:
            # Convert to Decimal for precision
            eur_amount = Decimal(str(amount_eur)).quantize(
                Decimal('0.01'), rounding=ROUND_DOWN
            )
            
            if eur_amount <= 0:
                raise ValueError("Amount must be greater than 0")
            
            print(f"\n🤖 ZCash DCA Bot")
            print(f"Target purchase: €{eur_amount}")
            print(f"Mode: {'DRY RUN (simulation)' if dry_run else 'LIVE'}")
            print("-" * 70)
            
            # Fetch current price
            current_price = self.kraken.get_current_price()
            print(f"\n📈 Current ZEC/EUR price: €{current_price}")
            
            # Calculate ZEC amount
            zec_amount = self.kraken.calculate_zec_amount(eur_amount, current_price)
            print(f"📊 Will buy approximately: {zec_amount} ZEC")
            
            if dry_run:
                # Simulate purchase
                print(f"\n🔍 DRY RUN - No actual purchase executed")
                
                purchase = PurchaseRecord(
                    date=datetime.now().isoformat(),
                    zec_bought=zec_amount,
                    eur_spent=eur_amount,
                    price_per_zec=current_price,
                    dry_run=True
                )
                
                # Don't save dry runs to tracker
                simulated_total = self.tracker.total_zec + zec_amount
                
                print(f"✓ Simulated purchase of {purchase.zec_bought} ZEC")
                print(f"✓ Would spend €{purchase.eur_spent}")
                print(f"✓ Simulated total: {simulated_total} ZEC")
                
                if post:
                    post_text = self.social.generate_post(purchase, simulated_total)
                    self.social.display_post(post_text)
                
                return {
                    'success': True,
                    'dry_run': True,
                    'purchase': purchase.to_dict(),
                    'simulated_total_zec': str(simulated_total)
                }
            
            else:
                # Execute real purchase
                print(f"\n💰 Executing market buy order...")
                
                order = self.kraken.execute_market_buy(zec_amount)
                
                # Extract actual filled values
                filled_zec = Decimal(str(order['filled']))
                cost_eur = Decimal(str(order['cost']))
                avg_price = (cost_eur / filled_zec).quantize(
                    Decimal('0.01'), rounding=ROUND_DOWN
                ) if filled_zec > 0 else current_price
                
                purchase = PurchaseRecord(
                    date=datetime.now().isoformat(),
                    zec_bought=filled_zec,
                    eur_spent=cost_eur,
                    price_per_zec=avg_price,
                    order_id=order.get('id'),
                    dry_run=False
                )
                
                # Save to tracker
                self.tracker.add_purchase(purchase)
                
                print(f"\n✅ Purchase successful!")
                print(f"✓ Bought: {purchase.zec_bought} ZEC")
                print(f"✓ Cost: €{purchase.eur_spent}")
                print(f"✓ Avg price: €{purchase.price_per_zec} per ZEC")
                print(f"✓ Order ID: {purchase.order_id}")
                print(f"💎 Total accumulated: {self.tracker.total_zec} ZEC")
                
                if post:
                    post_text = self.social.generate_post(
                        purchase,
                        self.tracker.total_zec
                    )
                    self.social.display_post(post_text)
                
                return {
                    'success': True,
                    'dry_run': False,
                    'purchase': purchase.to_dict(),
                    'total_zec': str(self.tracker.total_zec)
                }
        
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def stats(self) -> None:
        """Display accumulated statistics."""
        stats = self.tracker.get_stats()
        
        print("\n📈 ZCash Accumulation Statistics")
        print("=" * 70)
        print(f"Total ZEC accumulated: {stats['total_zec']} ZEC")
        print(f"Total EUR spent: €{stats['total_eur_spent']}")
        
        if stats['average_price']:
            print(f"Average price: €{stats['average_price']} per ZEC")
        
        print(f"Number of purchases: {stats['num_purchases']}")
        
        if stats['first_purchase']:
            first_date = datetime.fromisoformat(stats['first_purchase'])
            print(f"First purchase: {first_date.strftime('%Y-%m-%d %H:%M')}")
        
        if stats['last_purchase']:
            last_date = datetime.fromisoformat(stats['last_purchase'])
            print(f"Last purchase: {last_date.strftime('%Y-%m-%d %H:%M')}")
        
        # Show recent purchases
        if self.tracker.purchases:
            print(f"\n📋 Recent purchases (last 5):")
            recent = self.tracker.purchases[-5:]
            for p in reversed(recent):
                date_str = datetime.fromisoformat(p.date).strftime('%Y-%m-%d')
                print(f"  {date_str}: {p.zec_bought} ZEC @ €{p.price_per_zec}")
        
        print("=" * 70)


def main():
    """Entry point for Fire CLI."""
    fire.Fire(ZCashDCABot)


if __name__ == '__main__':
    main()
