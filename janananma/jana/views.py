from django.shortcuts import render, redirect
from django.db.models import Sum
from .models import DailyFinance, DailyPurchase, Wholesaler, BankTransaction, CreditTransaction
from django.utils import timezone
from datetime import date
from .forms import WholesalerForm
from django.db.models import Max
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib import messages
from collections import defaultdict
from calendar import monthrange
from datetime import datetime


def is_manager(user):
    return user.groups.filter(name='manager').exists()

def is_owner(user):
    return user.groups.filter(name='owner').exists()

class CustomLoginView(LoginView):
    template_name = 'login.html'

def home_page(request):
    form = AuthenticationForm()
    return render(request, 'dashboard/home_page.html', {'form': form})

def custom_logout(request):
    logout(request)  # Ends the session
    return redirect('/')  # Redirect to homepage

@login_required
@user_passes_test(is_owner)
def owner_manage_wholesalers(request):
    wholesalers = Wholesaler.objects.all()
    form = WholesalerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect('owner_manage_wholesalers')

    return render(request, 'dashboard/owner_wholesalers.html', {
        'form': form,
        'wholesalers': wholesalers
    })

def owner_dashboard(request):
    today = timezone.now().date()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    # Fetch entries for the selected month
    finance_entries = DailyFinance.objects.filter(date__month=month, date__year=year).order_by('date')
    purchase_entries = DailyPurchase.objects.filter(date__month=month, date__year=year)
    bank_entries = BankTransaction.objects.filter(date__month=month, date__year=year)

    # Aggregated totals
    summary = {
        'total_income': finance_entries.aggregate(total=Sum('sale_of_day'))['total'] or 0,
        'total_expenditure': finance_entries.aggregate(total=Sum('total_expenditure'))['total'] or 0,
        'total_purchase': purchase_entries.aggregate(total=Sum('bill_amount'))['total'] or 0,
        'total_credit_left': purchase_entries.aggregate(total=Sum('credit_left'))['total'] or 0,
        'total_staff_salary': finance_entries.aggregate(total=Sum('staff_salary'))['total'] or 0,
        'total_google_pay': finance_entries.aggregate(total=Sum('google_pay_income'))['total'] or 0,
        'total_other_income': finance_entries.aggregate(total=Sum('other_income'))['total'] or 0,
        'total_other_expenses': finance_entries.aggregate(total=Sum('other_expenditure'))['total'] or 0,
    }

    # Group purchases and banks by date
    daily_purchases = defaultdict(list)
    for p in purchase_entries:
        daily_purchases[p.date].append(p)

    daily_banks = defaultdict(list)
    for b in bank_entries:
        daily_banks[b.date].append(b)

    context = {
        'finance_entries': finance_entries,
        'daily_purchases': daily_purchases,
        'daily_banks': daily_banks,
        'summary': summary,
        'month': month,
        'year': year,
        'months': range(1, 13),
        'today': today,
    }

    return render(request, 'dashboard/owner_dashboard.html', context)

@login_required
@user_passes_test(is_manager)
def manager_purchase_entry(request):
    wholesalers = Wholesaler.objects.all()
    today = timezone.now().date()

    # Get previous credit for each wholesaler
    previous_credits = {}
    for wholesaler in wholesalers:
        last_purchase = DailyPurchase.objects.filter(wholesaler=wholesaler).order_by('-date').first()
        previous_credits[wholesaler.id] = last_purchase.credit_left if last_purchase else 0

    if request.method == "POST":
        for wholesaler in wholesalers:
            prefix = f"wholesaler_{wholesaler.id}_"
            previous_credit = request.POST.get(prefix + "previous_credit", 0)
            bill_number = request.POST.get(prefix + "bill_number")
            bill_amount = request.POST.get(prefix + "bill_amount", 0)
            paid_amount = request.POST.get(prefix + "paid_amount", 0)
            credit_left = request.POST.get(prefix + "credit_left", 0)

            if bill_number:  # Avoid empty rows
                DailyPurchase.objects.create(
                    date=today,
                    wholesaler=wholesaler,
                    previous_credit=previous_credit,
                    bill_number=bill_number,
                    bill_amount=bill_amount,
                    paid_amount=paid_amount,
                    credit_left=credit_left,
                )
        return redirect('manager_purchase_entry')

    return render(request, 'dashboard/manager_purchase_form.html', {
        "wholesalers": wholesalers,
        "previous_credits": previous_credits
    })

@login_required
@user_passes_test(is_manager)
def manager_daily_finance_entry(request):
    today = timezone.now().date()

    date_str = request.GET.get("date")
    if date_str:
        try:
            today = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            pass  # fallback to today's date if parsing fails

    # Check if entry exists for this date
    if DailyFinance.objects.filter(date=today).exists():
        messages.warning(request, f"Finance entry already exists for {today}")
        return redirect('manager-finance-summary')

    staff_members = ["Amila", "Ashwati", "Athira", "Arun", "Lijin", "Kannan"]
    credit_names = ["Amila", "Ashwati", "Athira", "Arun", "Lijin", "Kannan"]
    previous_credit = {}
    staff_list = ["Ashwati", "Athira", "Amila", "Arun", "Lijin", "Kannan", "Others"]

    # ✅ Correct: Fetch Previous Day Balance once outside the loop
    previous_finance = DailyFinance.objects.filter(date=today - timezone.timedelta(days=1)).first()
    previous_day_balance = previous_finance.balance if previous_finance else 0

    for staff in staff_list:
        total_credit = CreditTransaction.objects.filter(staff_name=staff).aggregate(total=Sum('credit_given'))['total'] or 0
        previous_credit[staff] = total_credit

    if request.method == "POST":
        # Capture all the POST data
        previous_balance = request.POST.get('previous_balance', 0)
        extra_cash = request.POST.get('extra_cash', 0)
        credit_paid_amila = request.POST.get('credit_paid_amila', 0)
        credit_paid_ashwati = request.POST.get('credit_paid_ashwati', 0)
        credit_paid_athira = request.POST.get('credit_paid_athira', 0)
        credit_paid_arun = request.POST.get('credit_paid_arun', 0)
        credit_paid_lijin = request.POST.get('credit_paid_lijin', 0)
        credit_paid_kannan = request.POST.get('credit_paid_kannan', 0)
        raajeev_income = request.POST.get('raajeev_income', 0)
        black_purse = request.POST.get('black_purse', 0)
        other_income = request.POST.get('other_income', 0)
        sale_of_day = request.POST.get('sale_of_day', 0)
        money_from_bank = request.POST.get('money_from_bank', 0)

        sip = request.POST.get('sip', 0)
        gokulam = request.POST.get('gokulam', 0)
        vijesh = request.POST.get('vijesh', 0)
        raajeev_expenditure = request.POST.get('raajeev_expenditure', 0)
        salary_amila = request.POST.get('salary_amila', 0)
        salary_ashwati = request.POST.get('salary_ashwati', 0)
        salary_athira = request.POST.get('salary_athira', 0)
        salary_arun = request.POST.get('salary_arun', 0)
        salary_lijin = request.POST.get('salary_lijin', 0)
        salary_kannan = request.POST.get('salary_kannan', 0)
        credit_to_amila = request.POST.get('credit_to_amila', 0)
        credit_to_ashwati = request.POST.get('credit_to_ashwati', 0)
        credit_to_athira = request.POST.get('credit_to_athira', 0)
        credit_to_arun = request.POST.get('credit_to_arun', 0)
        credit_to_lijin = request.POST.get('credit_to_lijin', 0)
        credit_to_kannan = request.POST.get('credit_to_kannan', 0)
        customer_credit = request.POST.get('customer_credit', 0)
        other_expenditure = request.POST.get('other_expenditure', 0)
        medicine_purchase = request.POST.get('medicine_purchase', 0)
        gpay_to_bank = request.POST.get('gpay_to_bank', 0)

        # Calculate totals
        total_income = (
            float(previous_balance) + float(extra_cash) +
            float(credit_paid_amila) + float(credit_paid_ashwati) + float(credit_paid_athira) +
            float(credit_paid_arun) + float(credit_paid_lijin) + float(credit_paid_kannan) +
            float(raajeev_income) + float(black_purse) + float(other_income) +
            float(money_from_bank) + float(sale_of_day)
        )

        total_expenditure = (
            float(sip) + float(gokulam) + float(vijesh) + float(raajeev_expenditure) +
            float(salary_amila) + float(salary_ashwati) + float(salary_athira) +
            float(salary_arun) + float(salary_lijin) + float(salary_kannan) +
            float(credit_to_amila) + float(credit_to_ashwati) + float(credit_to_athira) +
            float(credit_to_arun) + float(credit_to_lijin) + float(credit_to_kannan) +
            float(customer_credit) + float(other_expenditure) +
            float(medicine_purchase) + float(gpay_to_bank)
        )

        cash_balance = total_income - total_expenditure

        # Save in the model (adjust fields according to your DailyFinance model)
        DailyFinance.objects.create(
            date=today,
            previous_day_balance=previous_balance,
            extra_cash=extra_cash,
            money_from_bank=money_from_bank,
            credit_received=float(credit_paid_amila) + float(credit_paid_ashwati) + float(credit_paid_athira) +
                            float(credit_paid_arun) + float(credit_paid_lijin) + float(credit_paid_kannan),
            credit_given=0,  # capture separately if needed
            google_pay_income=request.POST.get('gpay_to_bank', 0),
            sale_of_day=sale_of_day,
            sip_paid=request.POST.get('sip', 0),
            chitty_paid=request.POST.get('vijesh', 0),
            staff_salary=float(salary_amila) + float(salary_ashwati) + float(salary_athira) +
                        float(salary_arun) + float(salary_lijin) + float(salary_kannan),
            credit_paid_out=float(credit_to_amila) + float(credit_to_ashwati) + float(credit_to_athira) +
                            float(credit_to_arun) + float(credit_to_lijin) + float(credit_to_kannan),
            other_income=other_income,
            other_expenditure=other_expenditure,
            medicine_return=medicine_purchase,
            purchase_paid=0,
            
        )


        # Save Bank Transactions
        transaction_types = request.POST.getlist('transaction_type')
        amounts = request.POST.getlist('amount')
        descriptions = request.POST.getlist('description')

        for transaction_type, amount, description in zip(transaction_types, amounts, descriptions):
            try:
                amount_float = float(amount)
                if amount_float > 0:
                    BankTransaction.objects.create(
                        date=today,
                        transaction_type=transaction_type,
                        amount=amount_float,
                        description=description
                    )
            except (ValueError, TypeError):
                continue

        # Save Credit Transactions only once
        for staff in staff_list:
            credit_field = f'credit_given_{staff.lower()}'
            credit_given = request.POST.get(credit_field, 0)
            try:
                credit_value = float(credit_given)
                if credit_value > 0:
                    CreditTransaction.objects.create(
                        date=today,
                        staff_name=staff,
                        credit_given=credit_value
                    )
            except (ValueError, TypeError):
                continue

        return redirect('manager-finance-summary')

    return render(request, 'dashboard/manager_daily_input.html', {
        'today': today,
        'staff_members': staff_members,
        'credit_names': credit_names,
        'previous_day_balance': previous_day_balance,
        'previous_credit': previous_credit,
    })

def manager_finance_summary(request):
    today = timezone.now().date()
    
    # Get selected month and year from GET params, or use current
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    finance_entries = DailyFinance.objects.filter(date__month=month, date__year=year).order_by('-date')
    bank_entries = BankTransaction.objects.filter(date__month=month, date__year=year)
    credit_entries = CreditTransaction.objects.filter(date__month=month, date__year=year)
    purchases = DailyPurchase.objects.filter(date__month=month, date__year=year)

    # Organize data by date
    daily_bank = defaultdict(list)
    for bank in bank_entries:
        daily_bank[bank.date].append(bank)

    daily_credit = defaultdict(list)
    for credit in credit_entries:
        daily_credit[credit.date].append(credit)

    daily_purchases = defaultdict(list)
    for p in purchases:
        daily_purchases[p.date].append(p)

    # Calculate missing dates
    days_in_month = monthrange(year, month)[1]
    all_dates = [timezone.datetime(year, month, day).date() for day in range(1, days_in_month + 1)]
    existing_dates = set(entry.date for entry in finance_entries)
    missing_dates = [d for d in all_dates if d not in existing_dates and d <= today]

    context = {
        'finance_entries': finance_entries,
        'daily_bank': daily_bank,
        'daily_credit': daily_credit,
        'daily_purchases': daily_purchases,
        'month': month,
        'year': year,
        'months': range(1, 13),
        'missing_dates': missing_dates,
        'today': today
    }
    return render(request, 'dashboard/manager_finance_summary.html', context)

@login_required
@user_passes_test(is_manager)
def edit_daily_finance(request, finance_id):
    finance_entry = DailyFinance.objects.get(id=finance_id)
    
    # Fetch bank transactions of THIS day's finance
    bank_transactions = BankTransaction.objects.filter(date=finance_entry.date)

    # Fetch credit transactions of THIS day's finance
    credit_transactions = CreditTransaction.objects.filter(date=finance_entry.date)

    credit_dict = {}
    for credit in credit_transactions:
        credit_dict[credit.staff_name] = credit.credit_given

    if request.method == "POST":
        # handle updating
        return redirect('manager-finance-summary')

    return render(request, 'dashboard/edit_daily_finance.html', {
        'finance_entry': finance_entry,
        'bank_transactions': bank_transactions,
        'credit_names': ['Ashwati', 'Athira', 'Amila', 'Arun', 'Lijin', 'Kannan'],
        'credit_dict': credit_dict,
    })


def delete_daily_finance(request, date_str):
    from datetime import datetime

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        DailyFinance.objects.filter(date=date_obj).delete()
        BankTransaction.objects.filter(date=date_obj).delete()
        CreditTransaction.objects.filter(date=date_obj).delete()
        messages.success(request, f"Deleted entries for {date_str}")
    except Exception as e:
        messages.error(request, f"Error deleting entry: {str(e)}")

    return redirect('owner_dashboard')