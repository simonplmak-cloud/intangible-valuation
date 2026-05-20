# Plan: Custom GitHub Pages Domain

## Approach
Two-part configuration:

### Part 1: GitHub Repo Side
1. Create `CNAME` file in repo root containing `intangible-valuation.simonmak.com`
2. Update `mkdocs.yml` `site_url` to the custom domain
3. Push changes — GitHub will detect the CNAME file and configure the custom domain

### Part 2: Vercel DNS Side
1. Add CNAME record in Vercel DNS: `intangible-valuation.simonmak.com` → `simonplmak-cloud.github.io`
2. This can be done via Vercel CLI (`vercel dns add`) or Vercel dashboard
3. DNS propagation takes up to 48 hours (typically minutes)

### Part 3: Verification
1. Confirm GitHub Pages recognizes the custom domain
2. Confirm HTTPS certificate is being provisioned
3. Test DNS resolution

## Risks
- DNS propagation delay (up to 48 hours)
- GitHub Pages HTTPS certificate provisioning delay (up to 24 hours)
- If Vercel CLI is not authenticated, DNS must be configured manually via dashboard

## Rollback
- Remove `CNAME` file from repo
- Remove CNAME DNS record from Vercel
- GitHub Pages reverts to `*.github.io` URL
