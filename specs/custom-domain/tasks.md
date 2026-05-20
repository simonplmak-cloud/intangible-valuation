# Tasks: Custom GitHub Pages Domain

## Gate 1: Repo Configuration
- [ ] Create `CNAME` file with `intangible-valuation.simonmak.com`
- [ ] Update `mkdocs.yml` `site_url` to `https://intangible-valuation.simonmak.com`
- [ ] Commit and push changes
- [ ] Verify GitHub Pages detects CNAME (check repo Settings → Pages)

## Gate 2: DNS Configuration
- [ ] Add CNAME record in Vercel DNS: `intangible-valuation` → `simonplmak-cloud.github.io`
  - Option A: Use `vercel dns add simonmak.com intangible-valuation CNAME simonplmak-cloud.github.io`
  - Option B: Configure manually via Vercel dashboard
- [ ] Verify DNS propagation: `dig intangible-valuation.simonmak.com CNAME`

## Gate 3: Verification
- [ ] Confirm GitHub Pages HTTPS certificate status
- [ ] Test `https://intangible-valuation.simonmak.com` resolves and serves docs
- [ ] Test HTTP → HTTPS redirect
- [ ] Verify no broken links or asset paths
