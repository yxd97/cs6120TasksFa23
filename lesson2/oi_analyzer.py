import sys, json

def load_bril_prog(path:str):
    with open(path, 'r') as f:
        prog = json.load(f)
    return prog


def print_help():
    print("Usage: python3 oi_analyzer.py <json file>")
    print("  Ananlyzes the operational intensity of each basic block in the program.")
    print("  Pointer arithmetics and function calls are ignored.")
    print("  Arguments:")
    print("    <json file>: A file contails the Bril program.")


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    file_path = sys.argv[1]
    prog = load_bril_prog(file_path)
    print(prog)

if __name__ == '__main__':
    main()