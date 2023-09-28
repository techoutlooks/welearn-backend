===============
welearn-backend
===============

Dev scrapbook for the weLearn app backend. weLearn's project docs can be found [here](https://techoutlooks.github.io/weLearn/).
weLearn is a Mobile eLearning platform from the TESS project.



Dev
--

pip install -U channels

Note: When using the dumpdata management command on polymorphic tables (or any table that has a reference to ContentType), include the --natural flag in the arguments. This makes sure the ContentType models will be referenced by name instead of their primary key as that changes between Django instances.
```shell script
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 books > fixtures/books-demo.json
python manage.py dumpdata --natural-foreign --natural-primary --indent 2 tess_core > fixtures/core-demo.json
```



Bootstrap app
--

```shell script
#rm db.sqlite3
python manage.py makemigrations tess_auth tess_pay tess_core  
python manage.py makemigrations books
python manage.py migrate easy_thumbnails
python manage.py migrate
```

pull world cities
pull django-money exchange rates (billed 1 request by call) from openexchangerates.org
```shell script
python manage.py cities_light --keep-slugs
python manage.py update_rates
```

```shell script
python manage.py loaddata fixtures/auth-demo.json
python manage.py loaddata fixtures/core-demo.json
python manage.py loaddata fixtures/books-demo.json

```


#### Place a subscription order 

a. `new_subscription_order()` to generate an unsaved `Transaction` (in-memory instance) from a
subscription, as follows
    ```
    
    yyyy/mm/dd sub_***** description
        subscriber:Payable                       amount
        provider:Receivable
    ```
    
#### Checkout 

Nota: Charges are concretely created only at checkout.
Checkout is initiated when an account (ie., BaseAccount subclass namely UserProfile, Org)  calls 
`checkout()`.  
The checkout process is two-fold through (1) `execute_order()` and (2) `ChargeManager.charge_customer()`
that eventually collects payment via a processor/backend.

checkout()->|-> BaseAccount.execute_order()     -> TransactionManager.record_order()
            |-> ChargeManager.charge_customer() -> ChargeManager.charge_card_one_processor()


###### BaseAccount.execute_order()

`record_order()` saves invoiced_items, a set of ``Transaction`` and update when
each associated ``Subscription`` ends.
    ```execute_order()
        -> TransactionManager.record_order()
    ```

###### ChargeManager.charge_customer()
    
    
#### Create a charge at subscription


#### Lock/un-lock access to service

This is achieved by using decorators.

```@requires_paid_subscription``` decorator through `fail_paid_subscription` uses the balance
on a subscription to determine when a subscription is locked (balance due) or unlocked (no balance).
```
@property
def is_locked(self):
    Charge.objects.settle_customer_payments(self.subscriber)
    balance = Transaction.objects.get_subscription_statement_balance(self)
    return balance > 0
```

#### Settle customer balance

`settle_customer_payments()` first queries the processor backend to attempt to settle charges into a
success or failed state (paid or not). This results in updating subscriber's balance with paid amounts.
```
def settle_customer_payments(self, accountable):
    for charge in self.in_progress_for_customer(accountable):
        charge.retrieve()
```

In other words, with each unpaid charge (ie. in-progress: **CREATED** namely; whereas a paid charge
has state **DONE**), if the charge was successfully paid through the payment processor, record the 
charge (or payment deposit) by creating a unique ``Transaction``.
The amount of the charge is then redistributed to the providers (minus processor fee). 
The sequence of calls:  
```
charge.retrieve()
    -> self.processor_backend.retrieve_charge(self)
        -> charge.payment_successful() 
            a) distribute_amount, processor_fee, broker_fee = \
                    self.processor_backend.charge_distribution()
               -> get_processor_charge()

            b) records Transactions for:
                - funds received by processor,
                - distribute_amount, processor_fee, broker_fee
```

TODO
--



FRONTEND
========

OK = EditTopics IonHeader > IonButton: reset, next, prev
= tag toggled refreshed component twice, useCallback/memo()?
OK = baseUrl of image fields
OK = set tutorial complete
= translate App to French
= pagination fetching via urql https://formidable.com/open-source/urql/docs/graphcache/computed-queries/#simple-pagination
OK BookItem stretching interferes with IonSearchbar => toggle IonSearchbar while stretching
OK = Filter by level
= Tags description unused
= Mandatory fields on profile?
OK TODO: edit location/city from EditBio
= Add Searchbar to BookFilter
= Profile page


= OPTIMIZE: all lists and selects with InfiniteScroll/VirtualScroll

* BUG: disabled menu on BookSearch page after completed tutorial
* BUG: total topics count on EditTopic page incorrect
* BUG: EditBio's city field not showing all cities

BACKEND
=======

= auto update num pages of book in admin
OK = Authors pictures
OK = Level model
= FIX dup filer images

PAYMENT
=======
= input validator for MoMo, OMoney deposit vouchers, fn(country, etc.)
= ask user if want to save payment details, add option for saving that in profile

https://ionicframework.com/docs/native/sms-retriever
https://developers.google.com/identity/sms-retriever/overview
https://enappd.com/blog/send-read-and-delete-sms-in-react-native/107/

**weLearn** will democratize access to educational content (both live and static) for high school students and upper.

Access to MoMo API for recurrent fee collection in Guinea.
Will integrate to existing mobile app through REST / OAuth v2.