# Sample LinkedIn Data - Alex Chen

This directory contains **fictional** LinkedIn export data for testing the Resume Builder application.

## Persona: Alex Chen

**Profile**: Staff Machine Learning Engineer with 12+ years of experience building ML systems at scale.

**Purpose**: This sample data allows developers and users to test the Resume Builder without using real personal information.

## Files

| File | Description |
|------|-------------|
| `Profile.csv` | Basic profile information (name, headline, summary) |
| `Positions.csv` | Work experience history (4 positions) |
| `Skills.csv` | Technical and soft skills (25 skills) |
| `Education.csv` | Educational background (2 degrees) |
| `Certifications.csv` | Professional certifications (3 certs) |
| `Projects.csv` | Notable projects (2 projects) |
| `Publications.csv` | Publications and articles (1 publication) |
| `Languages.csv` | Languages spoken (2 languages) |

## Data Authenticity

**⚠️ All data is completely fictional** - names, companies, dates, and details are made up for testing purposes only.

## CSV Format

Column headers match LinkedIn's actual data export format to ensure compatibility with the parser.

## Usage

```python
from resume_builder.parsers.linkedin import parse_profile

profile = parse_profile("sample_data/Profile.csv")
print(profile.full_name)  # "Alex Chen"
```
