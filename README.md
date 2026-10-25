# au-liquor-registers

Monthly snapshots of the Victorian and NSW liquor licence registers (public data, CC BY) and ABR entity names for the Principal Wine customer ABNs. Used to group venues by licensee and legal entity.

fetch.py downloads everything into data/. The GitHub Action in workflow-to-install/fetch.yml needs to be copied to .github/workflows/fetch.yml (the connector that pushed this repo lacks the workflow scope). It runs on push, on demand, and on the 3rd of each month.
