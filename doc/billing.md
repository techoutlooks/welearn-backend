

UserProfile.billing field hosts the billing settings of users, that includes available/active/default payment processors, subscriptions, funds balance, etc. 
Customer is either User or Org
Provider, Broker can only be Org.



Core
----
* Prepaid subscriptions to Plans
* GraphQL API to Lock/unlock access to service on Plan
* Multiple brokers per service on Plan
* Statement of accounts: Funds, Liabilities, Payables/Receivables, Backlogs
  for each party: Suscriber, Vendor, Broker (and payment Processor, internal).
  exportable to xls/csv
* Quota pricing

* Provider orgs, are products vendors
* Broker orgs, sell vendors products 
* Orgs subscribing to services sold by other orgs,
  as well as being themselves a provider.
* 3rd-party notification on new charge created


  
More
----
* Integrates several payment processors
* Money field with exchange rates


Accounting: Rules of the game
-----------------------------
- Pay (Funds out) only pre-recorded Expense
  Company: Where is my money going?
- Money received (Funds in) must be justified by a customer Liability counterpart,
  and Liabilities are subsequent to Receivable (reconciliable to Customer Payable)
  Finance inspectors: Are you laundering money? what is origin of funds?
    alright, double inspect at Customer's Payables will shed light!
- Receivable & Payable (resp. provider & subscriber) trace to Subscription (Plan purchased),
  or a refund (resp. subscriber, provider)    
Backlog: Product from transaction, piece of turnover,
            money not earned yet!
            
TODO
----
* Post paid subscriptions