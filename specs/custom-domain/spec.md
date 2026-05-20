# Spec: Custom GitHub Pages Domain

## Problem
GitHub Pages is served at `https://simonplmak-cloud.github.io/intangible-valuation/`. The project needs a professional custom domain `https://intangible-valuation.simonmak.com` for branding and discoverability.

## Requirements
- GitHub Pages must respond at `https://intangible-valuation.simonmak.com`
- HTTPS must be enforced (GitHub Pages provides automatic Let's Encrypt certs for custom domains)
- HTTP → HTTPS redirect must work
- The domain `simonmak.com` is managed via Vercel (repo: `../simonmak-website`)

## Constraints
- DNS is managed by Vercel for `simonmak.com`
- GitHub Pages repo: `simonplmak-cloud/intangible-valuation`
- Cannot modify Vercel DNS via API — must use Vercel CLI (`vercel dns`) or Vercel dashboard

## Acceptance Criteria
1. `CNAME` file exists in repo root with `intangible-valuation.simonmak.com`
2. `mkdocs.yml` `site_url` updated to `https://intangible-valuation.simonmak.com`
3. Vercel DNS has CNAME record: `intangible-valuation` → `simonplmak-cloud.github.io`
4. GitHub Pages custom domain configured in repo settings (or via CNAME file auto-detection)
5. HTTPS certificate provisioned by GitHub (automatic, may take up to 24 hours)
6. `https://intangible-valuation.simonmak.com` serves the docs site
