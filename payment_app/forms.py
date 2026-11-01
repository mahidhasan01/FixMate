from django import forms

from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'transaction_id']
        labels = {'payment_method': 'Payment method', 'transaction_id': 'TrxID'}
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9K7D2LX4QP'}),
        }
        error_messages = {
            'transaction_id': {'unique': 'This TrxID has already been used.'},
        }

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('payment_method')
        trx_id = cleaned_data.get('transaction_id')

        if method == Payment.CASH:
            cleaned_data['transaction_id'] = None
        elif not trx_id:
            self.add_error('transaction_id', 'Please enter the TrxID from your SMS.')
        return cleaned_data
