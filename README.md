# Vehicle number claim audit

This offline static audit compares documentation about judging vehicle identification numbers with Python call sites. It does not execute inspected code or contact a network. Install either distribution with pip and run:

```sh
vin-validation-claim-audit audit .
python3 -m vin_validation_claim_audit audit .
```

Use `--json` for structured output, `--verbose` for details, and repeat `--ignore PREFIX` to skip paths. The default threshold is high; `--fail-on medium` also fails for evidence found only in tests. Exit status 0 means the threshold passed, 2 means findings reached it, and 1 means a usage or input error.

Findings use these identifiers:

```
documented-vin-validation-claim-false
documented-no-vin-validation-claim-false
```

The scanner reads the root README and Markdown under docs, excluding fenced blocks. It normalizes case, whitespace, contractions and hyphens; inline code counts. It parses Python without running it, excludes symlinks and separates tests from production. Denials are removed before positive matching. It recognizes specific calls in vininfo, vin and pyvin, plus a defined set of generic named calls. A literal repair flag on the vin constructor is excluded. Each route must be present within one module.

## Differentiation

Generic validation asks whether input is checked at all. ISBN validation checks book numbers. ISSN validation checks serial numbers. IBAN validation checks bank account numbers. UUID validation checks unique identifiers. Semantic version validation checks version strings. MAC address validation checks hardware addresses. BIC validation checks bank identifier codes. Cron expression validation checks schedule strings. Cron expression description turns schedule strings into sentences. Scheduled execution runs jobs on a schedule. Date validation checks calendar dates. Timeout limits call duration. Payment processing takes payments. Card extraction reads card details from documents. Authentication can prove account ownership with a code or link. Password verification compares a password with a stored hash. Password hashing stores a hash. Password generation mints random passwords. PDF encryption protects a file. Email sending sends mail. SMS sending sends texts. Document extraction reads data from documents. Barcode scanning decodes codes from images. Email validation checks addresses. Phone number validation checks phone numbers. Password strength measures password quality. JSON Schema validation checks JSON data against a schema. Credit card validation checks card numbers and their Luhn digit. Domain validation checks host names. URL validation checks web addresses. IP address validation checks numeric addresses. JSON parsing decodes text into values. Regex matching finds patterns. URL parsing splits web addresses. Fetching retrieves a web address. DNS resolution looks up names. Barcode generation encodes account numbers. Account extraction reads account numbers from documents. Vehicle number extraction reads numbers from registration documents or images. Vehicle decoding interprets manufacturer, descriptor and identifier sections or looks up make, model and year. Vehicle history lookup retrieves a vehicle's past. These are distinct from judging the shape of a vehicle identification number.

Other families cover spreadsheet reading, spreadsheet generation, word-document reading, word-document generation, presentation reading, presentation generation, PDF extraction, PDF generation, PDF merging, PDF splitting, PDF rotation, PDF form-filling, PDF watermarking, PDF redaction, PDF compression, PDF annotation, table extraction, OCR, document extraction, e-signature, screen recording, video generation, QR code generation, barcode generation, barcode scanning, audio mixing, audio generation, audio editing, source separation, speech recognition, text-to-speech, noise suppression, music generation, and music transcription; their claims are outside these phrase lists.

## Limitations

```
validate vin
```

The bare phrase above is matched as a claim. A manual runbook step can use this wording without any implementation. This can be a false positive requiring human review.

```
vin validation
```

The bare phrase above is matched as a claim. A roadmap feature can use this wording before implementation. This can be a false positive requiring human review.

```
vin validator
```

The bare phrase above is matched as a claim. A hosted page can use this wording without local implementation. This can be a false positive requiring human review.

```
vin check
```

The bare phrase above is matched as a claim. A vehicle history service can use this wording for a lookup. This can be a false positive requiring human review.

```
check vin
```

The bare phrase above is matched as a claim. A manual runbook step can use this wording without code. This can be a false positive requiring human review.

```
verify vin
```

The bare phrase above is matched as a claim. An ownership identity step can use this wording. This can be a false positive requiring human review.

```
vin checksum
```

The bare phrase above is matched as a claim. A form field label can use this wording without a call. This can be a false positive requiring human review.

```
vin check digit
```

The bare phrase above is matched as a claim. A form field label can use this wording without a call. This can be a false positive requiring human review.

```
valid vin
```

The bare phrase above is matched as a claim. An example value can use this wording without a capability. This can be a false positive requiring human review.

```
vin is valid
```

The bare phrase above is matched as a claim. Example output can use this wording without a call. This can be a false positive requiring human review.

```
vehicle identification number validation
```

The bare phrase above is matched as a claim. A specification section can use this wording without code. This can be a false positive requiring human review.

```
validate vehicle identification number
```

The bare phrase above is matched as a claim. A manual runbook step can use this wording without code. This can be a false positive requiring human review.

```
vin verification
```

The bare phrase above is matched as a claim. An ownership identity step can use this wording. This can be a false positive requiring human review.

```
vin number check
```

The bare phrase above is matched as a claim. A history lookup can use this wording. This can be a false positive requiring human review.

```
vin format validation
```

The bare phrase above is matched as a claim. A format description can use this wording without a call. This can be a false positive requiring human review.

```
vin is invalid
```

The bare phrase above is matched as a claim. Example error output can use this wording without a call. This can be a false positive requiring human review.

```
vin validity
```

The bare phrase above is matched as a claim. A configuration flag or column can use this wording without a call. This can be a false positive requiring human review.

```
check vin number
```

The bare phrase above is matched as a claim. A history lookup can use this wording. This can be a false positive requiring human review.

```
vin checksum validation
```

The bare phrase above is matched as a claim. A specification section can use this wording without code. This can be a false positive requiring human review.

```
vin validation
```

The bare phrase above is matched as a claim. An external platform can use this wording for a result it produces. This can be a false positive requiring human review.

The incomplete wording below is deliberately omitted because it can refer to vehicle identity rather than a number.

```
validate vehicle identification
```

A constructor with `fix_check_digit=True` repairs the digit and is excluded.

A decode call or property read is excluded.

A pyvin network decode call is excluded.

A DecodedVIN construction is excluded.

A vehicle database lookup is excluded.

A WMI lookup is excluded.

Vehicle number extraction is excluded.

A history service lookup is excluded.

A regular expression match is excluded.

String rendering is excluded.

A method call on an unrecognized base may be missed.

A bare import is excluded.

Roadmaps and TODOs still count as documentation claims.

Unlisted denial wording may be missed.

Other documentation paths are not read.

Routes split across modules are missed.

Local definitions shadow route names.

Dead code counts.

External commands are excluded.

Generic input checks are excluded.

Email checks are excluded.

Phone checks are excluded.

URL checks are excluded.

IP address checks are excluded.

Domain checks are excluded.

ISBN checks are excluded.

ISSN checks are excluded.

IBAN checks are excluded.

UUID checks are excluded.

Semantic version checks are excluded.

MAC address checks are excluded.

BIC checks are excluded.

Cron expression checks are excluded.

Generic extraction is excluded.

Locally defined generic names are shadowed.

Alias chains may be missed.

Only exact wording is matched, so a paraphrase that avoids every listed wording is invisible to the claim side.

Only Python source is read.

Exact wording is required.

Other programming languages are invisible.

Dynamic imports and plugins are invisible.
