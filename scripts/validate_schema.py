import argparse
import json
import sys
import jsonschema

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--schema', required=True)
    parser.add_argument('--errorlog', required=True)
    args = parser.parse_args()

    try:
        with open(args.input, 'r') as f:
            data = json.load(f)
        with open(args.schema, 'r') as f:
            schema = json.load(f)

        jsonschema.validate(instance=data, schema=schema)
        print("Validation passed.")
        sys.exit(0)

    except jsonschema.ValidationError as e:
        msg = f"Validation error: {e.message}\nPath: {list(e.path)}"
        with open(args.errorlog, 'w') as f:
            f.write(msg)
        print(msg, file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        with open(args.errorlog, 'w') as f:
            f.write(msg)
        print(msg, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()