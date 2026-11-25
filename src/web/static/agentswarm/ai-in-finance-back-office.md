# What AI Has Actually Done for Finance Back Offices: Documented Cases, Failures and Lessons

## Why most finance-AI success stories need a label

Most of the cases in this post are vendor or consultant write-ups, not independent measurements.
A few are independent: a Stanford Graduate School of Business field study reported by Stanford GSB (Murray, 2025), and failures reported by journalists, such as the Financial Times and Associated Press wire reporting cited in the Codebridge record (Karpushin, 2026).
Each figure here carries one of three labels.
"Measured" means the source reports a result it measured, and we say who measured it.
"Claimed by [company or vendor]" means the number comes from the company that sells or built the system, and we name that company.
"Survey by [who, n=]" means a survey finding, where we give the surveyor and sample size; where the source gives no sample size, we write "n not given."
Dates are given where the source gives them.
Where a source gives no date, sample size or method, we say so and do not fill the gap.
Background: intelligent document processing (IDP) automates manual data entry from paper or document images into digital form, and IDP systems extract invoice data and enter it in the accounting system (AWS, n.d.).

## Accounts payable and invoice processing cases

Accounts payable (AP) receives supplier invoices, checks them against orders and receipts, and pays them.
All four write-ups below are vendor or service-provider claims, with no independent audit (Softtek, n.d.) (Auxis, n.d.) (Deloitte, n.d.) (Coupa, n.d.).

### Softtek: industrial manufacturer, $19M invoice backlog

- **Goal.** The client had about 2,000 open invoices worth $19 million, and more than 20% of payments were late (Softtek, n.d.).
- **Automated.** RPA handled intake, routing and approval triggers. AI agents handled extraction and four-way matching of purchase orders, invoices, goods receipts and delivery records. The legacy ERP limited integration (Softtek, n.d.).
- **Human approval.** Validation and approvals stayed with people, with human validation before posting (Softtek, n.d.).
- **Results (claimed by Softtek).** Cost per transaction down over 60%, 56% more monthly capacity, 60% fewer payment delays, and 80%+ of transactions with minimal human intervention (Softtek, n.d.).
- **Date and method.** None is given for the results (Softtek, n.d.).

### Auxis: West Coast specialty retailer

- **Goal.** Vendors kept putting the retailer's account on hold for late payments, and Auxis already ran its AP outsourcing (Auxis, n.d.).
- **Automated.** A UiPath Document Understanding workflow monitors a vendor mailbox, extracts invoice data and matches it to NetSuite purchase orders (Auxis, n.d.).
- **Human approval.** Invoices the workflow cannot validate go to Action Center for a person to resolve (Auxis, n.d.).
- **Results (claimed by Auxis).** 95% touchless processing for 20 vendors, and more than 40% more capacity with the same staff (Auxis, n.d.).
- **Date and method.** No date is given, and the source does not say how the 95% or 40% figures were measured (Auxis, n.d.).

### Deloitte: global consumer products company

- **Goal.** AP clerks spent time researching invoices before paying them, and processes lagged the company's growth (Deloitte, n.d.).
- **Automated.** Deloitte worked with the client on AP standardization, and Zora AI agents read invoices and recommend coding (Deloitte, n.d.).
- **Human approval.** Humans review and verify the agent's recommendations, and a confidence score shows when extra review is needed (Deloitte, n.d.).
- **Results (claimed by Deloitte).** A 92% touchless rate, processing time down 50%–75%, and invoice processing FTEs down 50% (Deloitte, n.d.).
- **Date and method.** The text gives a before-and-after comparison: up to 30 minutes per invoice before Zora AI (Deloitte, n.d.).
- **Date and method, continued.** It gives no measurement period or sample size (Deloitte, n.d.).

### Coupa: roundup of AP case studies

Coupa's post is dated April 10, 2026, and is written by its editorial team.
All eight cases are Coupa customers, so every metric is vendor-published (Coupa, n.d.).
I chose the cases with the clearest metrics.

- **GameStop.** Stated results: 82% increase in first-time match rate and 70% less average processing time. No date or method is given (Coupa, n.d.).
- **SUEZ.** Stated results: annual savings doubled to £15 million, with no period or method given (Coupa, n.d.).
- **Nationwide.** Stated results: 60% faster PO cycle time and 90%+ e-invoicing compliance. No baseline or period is given (Coupa, n.d.).
- **Molina Healthcare.** Stated results: 420% invoice growth with 10% more staff. No period is given (Coupa, n.d.).
- **Eurowag.** Stated results: 30% improvement in paid-on-time performance. No baseline or sample is given (Coupa, n.d.).

## Bookkeeping, accounting firms and the human-in-the-loop evidence

The Stanford GSB article on a study by Jung Ho Choi and Chloe Xie is dated June 26, 2025 (Murray, 2025).
The study used survey responses from 277 accountants and task-level data for 79 small- and mid-sized firms using AI-powered accounting tools (Murray, 2025).
Measured in the study, accountants using AI supported more clients per week and finalized monthly statements 7.5 days faster than those using traditional methods (Murray, 2025).
They also spent 8.5% less time on routine back-office processing (Murray, 2025).
The article reports a 12% rise in reporting granularity, which it presents as a quality measure (Murray, 2025).
The article gives no further method for these figures, and it does not say how quality was defined beyond granularity (Murray, 2025).
Its limits as reported: gains depended on experience, junior staff were more likely to accept flagged AI outputs, and the tools were mainly used for bookkeeping rather than audit, tax or valuation (Murray, 2025).

Codebridge, a vendor that builds AI agents for firms, published a list of accounting-firm cases (Karpushin, 2026).
Its small-firm cases draw on Journal of Accountancy interviews published in August 2026, in which named partners described the tool, build time and cost (Karpushin, 2026).
High Rock Accounting, an eight-person firm, built a client-feedback tool with Claude Code in four to five hours, at the cost of one team subscription plus low maintenance; the firm measured it (Karpushin, 2026).
Agate CPA, a six-person firm, reported conversions rising roughly 25% at minimal spend; the firm measured it (Karpushin, 2026).
Public Trust CPA, a sole proprietor, built an invoice-approval workflow in Microsoft Power Automate that creates QuickBooks bills only after client approval, at zero incremental cost (Karpushin, 2026).
The Wiss & Company case, about 450 accountants, reports up to 30% less manual time, a figure the article attributes to the vendor, not the firm (Karpushin, 2026).

Artsyl, a document-automation vendor, describes people reviewing exceptions and validating uncertain extracted data before it reaches downstream systems (Artsyl, n.d.).
Reviewers correct extracted values and approve them, and corrections can be fed back to the model as labelled examples (Artsyl, n.d.).
The article gives no measured results, trial dates or sample sizes, so its claims are vendor statements about design, not outcomes (Artsyl, n.d.).

## Reconciliation and month-end close

Month-end close is the process of finishing the books for a period, and reconciliation is checking that two records agree, such as a bank statement and the ledger.
Coupa, a vendor of AP software, publishes a roundup of customer case studies, so its figures are vendor claims, not independent measurements (Coupa, n.d.).
Coupa's Reddit case says the close went from 15 days to six days or less, a "60%" reduction, and that $6 million in total savings came over three quarters (Coupa, n.d.).
Coupa gives no measurement method, baseline date or independent check for either figure (Coupa, n.d.).
FP&A Trends (January 15, 2026) is a practitioner article with no measured case; it offers three approaches as guidance (FP&A Trends, n.d.).
The first is Python variance analysis, where a script computes actual-minus-budget variances and flags those above a 5% threshold (FP&A Trends, n.d.).
The second is rule-based account mapping in Python, where unmapped accounts are highlighted for review instead of being silently misclassified (FP&A Trends, n.d.).
The second also uses a GenAI tool to help write the mapping rules, and the author says "The LLM provides the script; you review and test it in your controlled environment" (FP&A Trends, n.d.).
The third uses GenAI to draft FP&A commentary, which the author says "can instantly generate a first draft" (FP&A Trends, n.d.).
Rework's guide describes bank reconciliation as pairing each bank line with its ledger entry, auto-clearing confident matches and sending uncertain ones to a person (Rework, n.d.).
Its three-band design (auto-match, suggest, exception) is a design guide with no measured results (Rework, n.d.).
J. SERVO argues that deterministic rules should handle exact matching, with LLMs limited to reading documents and drafting exception notes, because LLM outputs can vary between runs (J. SERVO, 2026).
J. SERVO cites a DualEntry benchmark of 77.3% top accuracy across AI models, and says it "could not" independently verify the methodology (J. SERVO, 2026).
Its 80–95% auto-match range is given as typical, with no source or sample (J. SERVO, 2026).
No documented expense-handling case appears in these sources; Rework lists an expense guide, "AI Expense Management: Receipt Capture, Policy Checks and Audits," in its navigation menu (Rework, n.d.).

## What went wrong or remains unproven

The Codebridge article reports ten documented cases: eight held and two were retracted or refunded, both at Big Four member firms (Karpushin, 2026).
The failure reporting comes from several outlets: Associated Press wire reporting and the *Financial Times* (Karpushin, 2026).
Codebridge says both failures involved AI-assisted reports with fabricated citations, not AP or reconciliation automation (Karpushin, 2026).
The first was Deloitte Australia, whose A$440,000 welfare compliance report contained fabricated references; Codebridge credits a University of Sydney researcher with finding them (Karpushin, 2026).
Deloitte agreed to repay the final instalment of its fee, and Codebridge says the handling drew more criticism than the errors (Karpushin, 2026).
The second was EY Canada, which withdrew a loyalty-programme fraud study in May 2026 after GPTZero found a non-existent McKinsey citation and unsupported footnotes; Codebridge says the Financial Times reported the findings (Karpushin, 2026).
Codebridge's own summary is that no public case automates a whole practice, only single workflows (Karpushin, 2026).
The "up to 30%" time reduction for Wiss & Company comes from the platform company and its model provider, not the firm (Karpushin, 2026).
JServo's headline 77.3% accuracy figure, from DualEntry, is one JServo says it could not independently verify (J. SERVO, 2026).
JServo's 10,000-transaction error example is hypothetical, and its "80–95% deterministic auto-match" range has no stated source, sample size or method (J. SERVO, 2026).
JServo says LLM runs can give different matches on identical inputs, but reports no measured sample for this risk (J. SERVO, 2026).
The Coupa and Softtek headline figures give no measurement method in the material reviewed (Coupa, n.d.) (Softtek, n.d.).
Codebridge reports a vendor shutdown separately from its cases: Botkeeper, an AI bookkeeping platform, announced its closure in February 2026 (Karpushin, 2026).

## What the cases have in common, and what an engineer should take from them

The goals met in these cases were fewer late payments, a smaller invoice backlog, faster close and higher throughput, but each was measured differently.
Softtek's industrial manufacturer reported a 60% reduction in payment delays and a 56% rise in monthly processing capacity without staffing growth; the page gives no date or method (Softtek, n.d.).
Deloitte's consumer products client reported a 92% touchless rate and a 50% cut in invoice processing FTEs, with no date or method stated (Deloitte, n.d.).
The Coupa close-time result and the $6M savings claim are vendor-published (Coupa, n.d.).
The Stanford GSB study is the most independent source here: survey responses from 277 accountants and task-level data for 79 firms showed a 7.5-day faster monthly close (Murray, 2025).
Most figures here come from the companies that sold or ran the work, and none of the vendor cases reports a control group.

Four design patterns recur.
Standardize the process first: Deloitte's client reestablished standard processes and controls before adding AI (Deloitte, n.d.).
Keep validation and approval with people: Softtek kept validation and approvals with staff and added human validation before posting (Softtek, n.d.).
Use deterministic rules for exact matching, with LLMs in assisting roles and flagged exceptions routed to people; JServo and FP&A Trends both describe this split, though JServo is an opinion piece and FP&A Trends is guidance, not a measured case (J. SERVO, 2026) (FP&A Trends, n.d.).
Automate one workflow rather than a whole function: Codebridge says the documented wins are narrow, with no public case of a firm automating a service line end to end (Karpushin, 2026).
Codebridge's gap in the public record is different: firms between roughly 50 and 200 people publish almost nothing (Karpushin, 2026).

A practical checklist for engineers:
- Record hours and error rates before and after deployment so ROI claims rest on observed data (J. SERVO, 2026).
- Log every match and decision for audit (J. SERVO, 2026).
- Flag unmapped or new accounts for review instead of silently misclassifying them (FP&A Trends, n.d.).
- Treat vendor numbers as claims until you can see the method and the date.

What remains unproven: none of these sources reports a controlled comparison against a baseline, most figures lack a date or sample size, and no expense-handling case is documented.

## References

- Amazon Web Services (n.d.). *What is Intelligent Document Processing (IDP)?*. AWS web page (aws.amazon.com).
- Artsyl (n.d.). *Human-in-the-Loop AI for Intelligent Document Automation*. Artsyl blog (artsyltech.com).
- Auxis (n.d.). *Accounts Payable Automation Case Study for Retailer*. Auxis case study (auxis.com).
- Coupa (n.d.). *8 AP Automation Case Studies That Drove ROI*. Coupa blog (coupa.com).
- Deloitte (n.d.). *Hands Off the Task, Eyes on the Outcome*. Deloitte US client story (deloitte.com).
- FP&A Trends (n.d.). *Three Practical Ways to Speed Up Month-End Closing with AI*. FP&A Trends (fpa-trends.com).
- J. SERVO Editorial Team (2026). *Reconciling Accounts: Where Deterministic AI Outperforms LLMs*. J. SERVO blog (jservo.com).
- Karpushin, K. (2026). *AI in Accounting Firms: 10 Documented Cases, Including the Ones That Failed*. Codebridge article (codebridge.tech).
- Murray, S. (2025). *AI Is Reshaping Accounting Jobs by Doing the "Boring" Stuff*. Stanford Graduate School of Business Insights.
- Rework (n.d.). *AI Bank Reconciliation: How Automated Matching Works*. Rework resources (resources.rework.com).
- Softtek (n.d.). *Using AI to get a $19M invoice backlog under control without loosening AP controls (AI-enabled accounts payable automation case study)*. Softtek case study (softtek.com).
