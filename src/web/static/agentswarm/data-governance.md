# Data Governance: A Thematic Literature Study for Practitioners

## Scope, sources and how to read the evidence

This study draws on eight documents of very different kinds, and they cannot be weighed equally[^1][^2][^3][^4][^5][^6][^7][^8].

The empirical studies are the Slovenian public-administration stewardship survey (Jukić et al., 2026), the PLS-SEM study of 98 GDPR-project professionals (Vojvodic & Hitz, 2022), and the systematic review of 2017–2023 literature (Bližnák et al., 2024)[^1][^2][^3].

The proposed works are the unified-theory synthesis (Osakwe, 2026), the real-time data-sharing research agenda (Sakhno et al., 2026), and the datasheets proposal for dataset documentation (Gebru et al., 2021)[^4][^5][^8].

The data mesh review synthesises 114 industrial gray literature articles, much of it promoting the concept, so its claims are advocacy or proposed architecture (Goedegebuure et al., 2024)[^6].

The SCHUFA commentary is a legal analysis of Article 22 GDPR (Aza, 2024)[^7].

Empirical means tested on data; proposed means a framework, model or template not yet tested; advocacy means practitioner or gray-literature promotion.

The corpus is small and uneven, and no source quotes DAMA-DMBOK directly, so any claim about it is second-hand.

## What data governance is: definitions, decision rights and frameworks

Data governance has no single settled definition, and the sources describe it as standards, policies, responsibilities and relations for managing data[^3].
The sources name decision rights and accountability as central to the definition[^3].
The Data Governance Institute defines data governance as a system of decision rights and accountabilities for information-related processes, specifying who can take what actions with what information, and when, under agreed-upon models[^3].

Definitions differ in scope.
The ISO/IEC 38505 standard places data governance as a subset of IT governance, whereas the DAMA (Data Management Association) practitioner definition treats it as a planning and control overlay over data management[^3].
Vojvodic and Hitz quote Weber et al. (2009) defining governance as the end-to-end distribution of decision rights and voting powers, responsibility acceptance and conflict resolution amongst stakeholders[^2].

Bližnák et al. reviewed 38 academic publications from 2017 to 2023 and report that the field has matured while definitions and outputs remain varied[^3].
The outputs include model designs, success factors and challenges, activity models and actor networks, and strategic principles[^3].
The review covered academic work only, so practitioner and institutional sources may be missing[^3].

Osakwe (2026) proposes a unified theory integrating regulatory compliance, data quality management, risk mitigation, organisational culture, technological infrastructure and stakeholder engagement[^4].
Its multi-layered architecture has four layers: strategic, tactical, operational and technical[^4].
The theory is proposed rather than tested, and it rests on a synthesis of 87 peer-reviewed articles, 12 industry reports and 8 regulatory documents[^4].
Osakwe mentions the DAMA body of knowledge only descriptively, so the corpus says little about DAMA-DMBOK or comparable frameworks[^4].

Sakhno et al. extend governance to real-time data sharing frameworks, which they define as socio-technical systems enabling continuous, low-latency exchange of information across organisational, sectoral or jurisdictional boundaries[^5].
They contrast centralised platform models with distributed consortia, noting that centralised models may gain efficiency while losing contestability[^5].
Their central claim is that distributing computation does not eliminate questions of control and accountability but reconfigures them in less visible ways[^5].
The report rests on an interpretive panel analysis and polling of eighteen participants, so its governance claims are research directions rather than tested findings[^5].

The sources agree that governance is multi-dimensional and that accountability must be assigned explicitly[^2][^4].
They differ on scope, on how prescriptive governance should be, and on whether one integrated model is feasible or desirable.
Vojvodic and Hitz treat compliance spending as a possible source of value, whereas Osakwe describes regulatory compliance as a fundamental driver of governance initiatives[^2][^4].

## Organisational models: centralised, federated and data mesh

Centralised data architectures are the baseline that data mesh is positioned against[^6].
In these architectures a central team collects, processes and manages domain data, and the review argues that this team becomes a bottleneck, so responsibility should move to domain teams[^6].
Data mesh is the decentralised alternative examined in a review of 114 industrial gray literature articles, which notes a lack of academic definitions of the concept[^6].

Data mesh rests on four principles: data as a product, domain ownership of data, a self-serve data platform, and federated computational governance[^6].
In the review's account, a data product is an architectural quantum, an independently deployable component that bundles data and metadata, code, and infrastructure, while some sources treat a curated data set alone as a data product[^6].
Domain ownership draws on domain-driven design (DDD), which decomposes business functions into domains aligned with organisational units, and domain teams build data products and carry out domain-level governance[^6].
Under federated computational governance, a federated team sets global standards for interoperability and compliance, and balancing central control against domain autonomy is difficult[^6].
The gray literature names roles such as data platform teams, product owners, product developers and federated governance teams, and the authors add a product aggregator role themselves[^6].

Practitioners present data mesh as suited to organisations with a large, diverse data landscape or a need for agility, and as unsuited where domain orientation, governance or platform maturity is low[^6].
The challenges named include complexity, interoperability problems for organisations using multiple clouds, duplicated effort, technical debt and a shortage of experienced data engineers[^6].
The authors map findings onto three reference architectures adapted from service-oriented architecture (SOA), which they relate to microservices, but present them as guides rather than tested designs[^6].

The evidence base is gray literature, much of it promoting the concept, so the benefit claims are advocacy or proposed architecture rather than shown effects[^6].
The authors note that few complete, holistic architecture instances exist to compare with, and many sources only consider partial architectures[^6].
Bližnák et al. do not discuss data mesh, but note that the governance literature leaves open how governance works beyond the boundaries of one organisation[^3].
Sakhno et al. argue that distributing computation does not remove governance and trust challenges but relocates them[^5].
None of these sources says when to centralise and when to federate.

## Data quality and stewardship

Data stewardship spans data management, documentation, preservation and access throughout the lifecycle, but the role remains heterogeneous and not fully standardised[^1].
Empirical evidence comes from an online survey of Slovenian public administration with 96 responses included in the analysis[^1].
Jukić et al. report stewardship as present but weakly institutionalised, usually an additional task rather than a formal role, and mainly operational (collection, verification and user support) rather than strategic[^1].
Most respondents (66%) devoted up to 10% of their working time to these tasks; training needs were high, particularly in legal compliance, data quality standards and opening data[^1].
No response rate could be calculated, and the authors caution that data are self-reported and may include several respondents from one organisation[^1].

Osakwe's proposed unified theory places stewardship and quality management in the operational layer of a four-layer governance architecture[^4].
Bližnák et al. find data quality the most frequently mentioned decision domain across reviewed studies, although their counts are approximate[^3].
Gebru et al. propose datasheets documenting dataset motivation, composition, collection, uses and maintenance to increase transparency and accountability[^8].
The proposal draws on testing on two datasets and product-team feedback; reported impact concerns adoption and pilots rather than measured quality effects[^8].

Osakwe's review describes quality management as requiring clear ownership, and master data management as requiring defined ownership and stewardship responsibilities[^4].
The framework describes stewards as responsible for specific data domains[^4].
The survey found stewardship performed ad hoc across diverse roles and units, without a clearly defined organisational home[^1].

## Privacy, compliance and regulation

Data governance meets regulation most directly through privacy compliance.
Vojvodic and Hitz (2022) surveyed 98 data-management professionals involved in recent EU GDPR projects in larger European organisations and analysed the responses with partial least squares structural equation modelling (PLS-SEM), a method that estimates links between constructs, which are unobserved concepts measured through survey items[^2].
Data Governance Span, the extent of business-stakeholder involvement (vertical) and cross-functional coordination (horizontal), was associated with higher Privacy Project Efficiency and with higher Data Compliance Innovation[^2].
The effect on efficiency was stronger (path coefficient 0.502) than the effect on innovation (0.378), and Customer-Centric Orientation fully mediated the innovation effect[^2].
The data are self-reported, cross-sectional, drawn from one regulation and from larger firms, with a small sample and single-item measures for innovation and efficiency, and the authors note that regional and industry differences may be a topic for a more narrowly defined study[^2].
Osakwe (2026) treats regulatory compliance as one of six interconnected dimensions of an integrated governance model, alongside data quality, risk, culture, technology and stakeholder engagement[^4].
Sakhno et al. (2026) propose regulatory stewardship, consent architectures, liability allocation and RegTech (technology that automates regulatory compliance) as design patterns for data sharing, but these are proposed designs rather than tested practices[^5].

The legal angle comes from the Court of Justice of the European Union's SCHUFA judgment, which Aza (2024) analyses for its effect on Article 22 GDPR, the right not to be subject to a decision based solely on automated processing that significantly affects a person[^7].
The Court held that a probability value such as a credit score can itself be a decision where three cumulative conditions are met: a decision exists, it is based solely on automated processing including profiling, and it produces legal or similarly significant effects[^7].
A third party that draws strongly on the score can satisfy the third condition, so the score's issuer can fall under the rule even where a bank takes the final action[^7].
Assessing the meaningfulness of human intervention is one of the most disputed areas in the case law, and Aza also notes that the judgment leaves open whether predictive as well as actual harms are covered[^7].

Agreement that compliance belongs inside governance rests on Osakwe's synthesis, in which regulatory compliance is interconnected with other governance dimensions[^4].
Whether compliance is a cost or a source of value is disputed, and Vojvodic and Hitz (2022) argue that compliance spending can yield competitive value, a claim supported by a survey association rather than outcome measurement[^2].

## Governing data for AI and machine learning

Gebru et al. propose datasheets for datasets, a standard way to document machine learning datasets, because no standardised documentation process existed for them[^8].
A datasheet would record a dataset's motivation, composition, collection process, recommended uses and maintenance, with the stated aims of transparency, accountability and reduced unwanted bias[^8].
The authors present this as a proposal drawn from documentation practice in the electronics industry and from consultation with dataset creators, researchers and lawyers, and they report early pilots within several companies[^8].
The paper gives no measured effects of datasheets, and it does not report such evidence.

Aza analyses the CJEU's SCHUFA ruling, in which a probability value such as a credit score can fall under Article 22 GDPR when a third party draws strongly on it[^7].
Article 22(1) gives a right not to be subject to a decision based solely on automated processing that legally or similarly significantly affects a person, and the CJEU read it as a prohibition in principle[^7].
Aza argues that the ruling may reach workplace tools that score workers, and that Article 22(3) safeguards include the right to obtain human intervention[^7].
Whether human involvement is meaningful, and whether predictive as well as actual harms are covered, remain unresolved[^7].
For governance, automated scoring therefore carries legal exposure and requires human involvement that is real rather than nominal.

Bližnák et al. link the 2023 peak in data governance publications to AI emerging as a key application domain[^3].
Sakhno et al. extend the question to real-time data sharing, where federated intelligence moves control to model aggregation and leaves unclear who is responsible for outcomes and who can explain or contest a decision[^5].
This is presented as a research agenda with proposed questions and methods, not tested findings[^5].
None of the empirical studies in this corpus tests AI-specific governance, so this theme rests on one legal analysis, one documentation proposal and one research agenda, and it is the thinnest on evidence of the themes reviewed.

## Comparing the main approaches side by side

Read together, the approaches answer different questions at different levels, and the sources do not rank them against each other.

- Integrated framework (Osakwe, 2026): six dimensions are treated as one interdependent system, and four layers (strategic, tactical, operational, technical) each serve distinct functions; it is a proposed theory built from a literature synthesis[^4].
- Review-derived definition (Bližnák et al., 2024): data governance is defined as decision rights and accountabilities; the field remains ambiguous; the evidence is a review of 38 publications, most of them conceptual[^3].
- Data mesh (Goedegebuure et al., 2024): domain teams own data products under federated computational governance; advocacy and proposed architecture from 114 gray-literature articles; no controlled comparison of outcomes[^6].
- Stewardship as practised (Jukić et al., 2026): stewardship is present but weakly institutionalised and largely operational; empirical survey of 96 Slovenian respondents, self-reported[^1].
- Compliance-driven governance (Vojvodic & Hitz, 2022): governance span improves privacy project efficiency and compliance innovation; empirical PLS-SEM study of 98 professionals on EU GDPR projects, one regulation[^2].
- Automated scoring (Aza, 2024): a score can count as an automated decision under Article 22 GDPR; legal analysis of one CJEU judgment, not a measurement of effects[^7].
- Dataset documentation (Gebru et al., 2021): standard documentation of motivation, composition and maintenance; proposed template[^8].
- Data-sharing governance (Sakhno et al., 2026): trust, security and accountability across organisations sharing data in real time; a research agenda from an expert panel[^5].

Sakhno et al. extend accountability beyond a single firm, asking who is responsible for outcomes as governance is enacted across organisational and jurisdictional boundaries[^5].
Osakwe's layers and Jukić et al.'s operational stewardship both concern day-to-day data work, although the survey does not test the layered model[^4][^1].
The sources support few direct comparisons: none compares centralised and federated models on outcomes, and none tests a unified framework against alternatives[^6][^4].
Vojvodic and Hitz is the only quantitative test of a governance practice in this set, while Aza is a legal reading[^2][^7].

## What remains open or under-researched

The sources leave several gaps visible, and most concern evidence rather than ideas.
Goedegebuure et al. report that no tools and no detailed, empirically validated methodologies exist for applying data mesh principles, and they call for more studies of organisational impacts and barriers to adoption[^6].
Osakwe's unified model has not been tested empirically[^4].
Jukić et al. rest their stewardship account on one national, self-reported survey of 96 responses[^1].
Vojvodic and Hitz name one regulation, a cross-sectional design, larger firms, and untested regional and industry differences as limits[^2].
No empirical study in the corpus tests AI or machine-learning governance, and Gebru et al. do not measure whether dataset documentation works in practice[^8].
Aza's commentary says the SCHUFA judgment brings scoring within the ambit of Article 22 GDPR, but the scope of Article 22(1) is often hazy[^7].
Sakhno et al. set out a research agenda on trust, security, power distribution and governance-by-design in real-time data sharing[^5].
Their panel poll, in which 67% of audience members ranked transparent governance as the most important factor, drew on a small, mainly academic audience rather than a representative sample[^5].
Bližnák et al. find no consensus on the definition of data governance, including its overlaps with information governance and data management[^3].
Their review excluded practitioner and institutional publications, which might have led to some omissions in the state of the art[^3].

## Summary: practical implications and research gaps

Public-sector stewardship is present but weakly institutionalised, with the largest training gaps in legal compliance, data quality standards and opening data[^1].

- Formalising stewardship roles and training is supported by empirical evidence from a single national public sector; the authors urge caution because the data are self-reported and several respondents may come from one organisation[^1].
- Treating compliance as an integrated governance capability that can yield efficiency rests on one empirical study of 98 professionals, in which the efficiency effect was stronger than the innovation effect[^2].
- Caution on data mesh claims is warranted, because the benefit claims come from 114 gray-literature articles that report practitioners' perspectives[^6].
- Documenting ML datasets is a proposal, with datasheets offered to increase transparency and accountability[^8].
- Automated-decision rules need watching, because the SCHUFA judgment treats a score as a decision under Article 22 GDPR[^7].

Main research gaps: tested outcomes for data mesh; stewardship evidence beyond one national survey; compliance effects across regulations, regions and industries; whether dataset documentation works in practice; and legal limits on automated scoring.

## References

[^1]: Jukić, T., Vrbek, S., Keržič, D. (2026). *(Open) Data Stewardship in the Public Sector: Evidence from a Survey of Slovenian Public Administration*. 39th Bled eConference: Co-creating Human-Centred and Responsible Digital Futures. Cited at pages 1, 3, 6, 7, 8, 11, 12.
[^2]: Vojvodic, M., Hitz, C. (2022). *Relation of Data Governance, Customer-Centricity and Data Processing Compliance*. Cited at pages 1, 2, 6, 29.
[^3]: Bližnák, K., Munk, M., Pilková, A. (2024). *A Systematic Review of Recent Literature on Data Governance (2017–2023)*. IEEE Access. Cited at pages 1, 2, 5, 8, 11, 13.
[^4]: Osakwe, J. (2026). *A Unified Theory of Data Governance: Integrating Frameworks for Enhanced Data Protection and Compliance*. International Journal of Information Security (IJIS), Volume 5, Issue 1. Cited at pages 1, 3, 6, 7, 8.
[^5]: Sakhno, A., Gewald, H., Gupta, A., Järveläinen, J., McCarthy, S., Morgan, L. (2026). *Real-Time Data Sharing Frameworks – Current State and Research Agenda*. Communications of the Association for Information Systems, 59 (in press). Cited at pages 1, 6, 7, 10, 18, 19.
[^6]: Goedegebuure, A., Kumara, I., Driessen, S., van den Heuvel, W.-J., Monsieur, G., Tamburri, D. A., Di Nucci, D. (2024). *Data Mesh: A Systematic Gray Literature Review*. arXiv preprint arXiv:2304.01062v3. Cited at pages 1, 26.
[^7]:  (2024). *Scores as Decisions? Article 22 GDPR and the Judgment of the CJEU in SCHUFA Holding (Scoring) in the Labour Context*. Industrial Law Journal, Vol. 53, No. 4. Cited at pages 1, 6, 7, 11, 12, 16, 18.
[^8]: Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J. W., Wallach, H., Daumé III, H., Crawford, K. (2021). *Datasheets for Datasets*. arXiv preprint arXiv:1803.09010v8. Cited at pages 1, 2, 3, 4, 10, 11.
