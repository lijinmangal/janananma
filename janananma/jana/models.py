from django.db import models
from django.utils import timezone

class Wholesaler(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class DailyPurchase(models.Model):
    date = models.DateField(default=timezone.now)
    wholesaler = models.ForeignKey(Wholesaler, on_delete=models.CASCADE)
    previous_credit = models.DecimalField(max_digits=10, decimal_places=2)
    bill_number = models.CharField(max_length=50)
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    credit_left = models.DecimalField(max_digits=10, decimal_places=2)

class DailyFinance(models.Model):
    
    date = models.DateField(default=timezone.now)
    previous_day_balance = models.DecimalField(max_digits=10, decimal_places=2)
    money_from_bank = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_received = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_given = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    google_pay_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_of_day = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    other_income = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sip_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    staff_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    chitty_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credit_paid_out = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    other_expenditure = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    medicine_return = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchase_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    extra_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def total_income(self):
        return (
             (self.previous_day_balance or 0) + (self.money_from_bank or 0) + (self.credit_received or 0) + 
             (self.credit_given or 0) + (self.google_pay_income or 0) + (self.sale_of_day or 0) + (self.other_income or 0)
        )

    @property
    def total_expenditure(self):
        return (
            (self.sip_paid or 0)+ (self.staff_salary or 0 )+
            (self.chitty_paid or 0) + (self.credit_paid_out or 0) +
            (self.other_expenditure or 0) + (self.medicine_return or 0) +
            (self.purchase_paid or 0)
        )

    @property
    def balance(self):
        return self.total_income - self.total_expenditure

class MonthlySummary(models.Model):
    month = models.DateField()
    total_income = models.DecimalField(max_digits=12, decimal_places=2)
    total_expenditure = models.DecimalField(max_digits=12, decimal_places=2)
    total_purchase = models.DecimalField(max_digits=12, decimal_places=2)
    total_credit_paid = models.DecimalField(max_digits=12, decimal_places=2)
    total_credit_left = models.DecimalField(max_digits=12, decimal_places=2)
    total_google_pay = models.DecimalField(max_digits=12, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2)

from django.db import models

class BankTransaction(models.Model):
    date = models.DateField()
    transaction_type = models.CharField(max_length=20, choices=(('Income', 'Income'), ('Expenditure', 'Expenditure')))
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.transaction_type} - ₹{self.amount}"
    
class CreditTransaction(models.Model):
    date = models.DateField()
    staff_name = models.CharField(max_length=100)
    credit_given = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.date} - {self.staff_name} - ₹{self.credit_given}"

