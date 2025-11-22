# Examples

This directory contains example data and test cases for the customer support system.

## Test Tickets

- `test_ticket.json`: Example customer support ticket

## Usage

### Testing Asya Implementation

```bash
# Send a test ticket to Asya (requires Asya gateway or direct queue access)
python scripts/send_test_ticket.py --framework asya --ticket examples/test_ticket.json
```

### Testing Ray Serve Implementation

```bash
# Send a test ticket to Ray Serve
python scripts/send_test_ticket.py --framework ray --ticket examples/test_ticket.json
```

