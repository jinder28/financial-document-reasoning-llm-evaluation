# Third-party material and attribution

## SEC filings and derived text

The source corpus is derived from public SEC EDGAR Form 10-K filings for Apple, Amazon, JPMorgan Chase, Bank of America, Verizon and Ford. Cleaned filing text, excerpts within locked retrieval contexts and quoted model-response evidence are included for study inspection and reproducibility. They are **not represented as original corporate disclosures authored by the dissertation author**.

The exact filing identifiers and source links are recorded in [Appendix C](docs/appendices/Appendix_C_Dataset_and_Claim_Case_Register_Final.pdf) with matching identifiers in the [locked execution queue](inputs/queue/api_execution_queue_locked_v1_amendment001.csv). The [derived source register](docs/provenance/filing-sources.csv) combines the queue's identifiers with the actual SEC hyperlink targets in Appendix C; it does not replace those originals.

The SEC's [Privacy Information — Website Dissemination](https://www.sec.gov/about/privacy-information) states that information provided on its site may be copied or distributed without SEC permission and asks that the SEC be cited as the source. This notice does not claim that the author owns third-party material or can waive every separate copyright, trademark or other right. SEC seals, logos and agency artwork are not being adopted as branding for this project.

Claims are research evaluation items, not allegations or audit findings about these companies. Company and product names identify the study inputs and dependencies; no endorsement or affiliation is implied.

## Research literature and software dependencies

Referenced publications are attributed in the dissertation, Appendix A1 and the citation-control workbook. Full third-party research papers are not packaged in the repository. Refer to each publisher or author for reuse permissions.

The dependency names in `requirements.txt` and the referenced container base image are governed by their respective upstream licences and terms. Their installation instructions do not transfer their ownership to this project. OpenAI model responses are retained experimental outputs, not a claim of ownership over the underlying model or service.

## This repository's licence status

No MIT, Apache, Creative Commons or other open-source licence has been applied to this publication package. Public inspectability is distinct from permission for unrestricted reuse. The author can select separate terms for original code and report content after confirming the rights held; those terms cannot relicense third-party material beyond the rights available.

GitHub explains the distinction in its [licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository), including the ability of users to view and fork public repositories under GitHub's terms. Do not describe this repository as “open source” until an appropriate licence is actually added.
