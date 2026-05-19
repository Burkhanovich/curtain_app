from .models import Curtain

CART_SESSION_KEY = 'cart'


class Cart:
    """Session asosida savat"""

    def __init__(self, request):
        self.session = request.session
        self._cart = self.session.setdefault(CART_SESSION_KEY, {})

    def _save(self):
        self.session.modified = True

    def add(self, curtain, quantity=1):
        key = str(curtain.pk)
        if key in self._cart:
            self._cart[key]['quantity'] += quantity
        else:
            self._cart[key] = {
                'quantity': quantity,
                'price': curtain.final_price,
            }
        self._save()

    def remove(self, curtain_id):
        key = str(curtain_id)
        if key in self._cart:
            del self._cart[key]
            self._save()

    def update_quantity(self, curtain_id, quantity):
        key = str(curtain_id)
        if key in self._cart:
            if quantity > 0:
                self._cart[key]['quantity'] = quantity
            else:
                del self._cart[key]
            self._save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.session.modified = True
        self._cart = self.session[CART_SESSION_KEY]

    def __iter__(self):
        curtain_ids = list(self._cart.keys())
        curtains = Curtain.objects.filter(pk__in=curtain_ids).prefetch_related('images')
        curtain_map = {str(c.pk): c for c in curtains}
        for key, item in self._cart.items():
            curtain = curtain_map.get(key)
            if curtain:
                yield {
                    'curtain': curtain,
                    'quantity': item['quantity'],
                    'price': item['price'],
                    'total_price': item['quantity'] * item['price'],
                }

    def __len__(self):
        return sum(item['quantity'] for item in self._cart.values())

    def get_total(self):
        return sum(item['quantity'] * item['price'] for item in self._cart.values())
