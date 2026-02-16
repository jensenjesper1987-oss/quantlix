# Security

## Reporting vulnerabilities

If you discover a security vulnerability, please report it responsibly.

**Do not** open a public GitHub issue for security vulnerabilities.

Instead:

1. **Report** via GitHub Security Advisories (Repository → Security → Advisories) or email the maintainers at jensen.jesper1987@gmail.com
2. **Include** a description of the vulnerability and steps to reproduce
3. **Allow** time for a fix before public disclosure (we aim for 90 days or less)

We will acknowledge receipt and work with you on a fix and disclosure timeline.

## Security practices

- **Secrets**: Never commit `.env`, `terraform.tfvars`, `kubeconfig*.yaml`, or API keys. Use `.env.example` as a template.
- **Dependencies**: Keep dependencies updated. Run `pip audit` and `npm audit` periodically.
- **Production**: Use strong passwords, rotate secrets, and follow [docs/GO_LIVE.md](docs/GO_LIVE.md) for deployment.
