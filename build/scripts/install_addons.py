import sys
import os
import argparse
import subprocess

def is_valid_odoo_module_path(path):
    """Check if the provided path is a valid Odoo module directory (contains __manifest__.py or __openerp__.py)."""
    return any(os.path.isfile(os.path.join(path, f)) for f in ["__manifest__.py", "__openerp__.py"])

def find_odoo_paths(addons_path):
    """Recursively find valid Odoo modules in the specified path and return their parent paths."""
    valid_paths = set()  # Use a set to avoid duplicates
    for root, dirs, files in os.walk(addons_path):
        if is_valid_odoo_module_path(root):
            # Add the parent directory of the valid module
            valid_paths.add(os.path.dirname(root))
    return list(valid_paths)

def find_odoo_modules(addons_path):
    """Recursively find valid Odoo modules in the specified path and return their names."""
    valid_modules = []
    for root, dirs, files in os.walk(addons_path):
        if is_valid_odoo_module_path(root):
            # Get the module name by stripping everything before the last '/'
            module_name = os.path.basename(root)
            valid_modules.append(module_name)
    return valid_modules

def main():
    parser = argparse.ArgumentParser(description="Install and Run Odoo with custom modules and DB settings")
    parser.add_argument("--addons-path", required=True, help="Comma-separated list of add-ons paths to check and install modules from")
    parser.add_argument("--db-name", required=True, help="Database name for Odoo")
    parser.add_argument("--db-user", required=True, help="Database user for Odoo")
    parser.add_argument("--db-password", required=True, help="Database password for Odoo")
    parser.add_argument("--db-host", default="localhost", help="Database host for Odoo (default: localhost)")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install", action="store_true", help="Install all found modules and stop after initialization")
    group.add_argument("--run-odoo", action="store_true", help="Run Odoo server without stopping after initialization")
    group.add_argument("--shell", action="store_true", help="Run Odoo in shell mode")
    group.add_argument("-u", "--update", metavar="MODULE", help="Update a specific Odoo module")

    args = parser.parse_args()

    # Validate and collect add-on paths
    all_addon_paths = []
    all_modules = []
    for path in args.addons_path.split(","):
        if not os.path.isdir(path):
            print(f"Skipping invalid path: {path}")
            continue
        valid_paths = find_odoo_paths(path)
        if valid_paths:
            all_addon_paths.extend(valid_paths)
            all_modules.extend(find_odoo_modules(path))
        else:
            print(f"No valid Odoo modules found in: {path}")

    # Set environment variables for the database
    os.environ["PGDATABASE"] = args.db_name
    os.environ["PGUSER"] = args.db_user
    os.environ["PGPASSWORD"] = args.db_password
    os.environ["PGHOST"] = args.db_host

    # Common base command for Odoo
    addons_path_arg = ",".join(all_addon_paths)
    base_command = [
        "python3", "/odoo/odoo-bin",
        f"--addons-path=/odoo/addons,{addons_path_arg}",
        f"--db_user={args.db_user}",
        f"--db_password={args.db_password}",
        f"--db_host={args.db_host}",
        f"--database={args.db_name}"
    ]

    try:
        if args.install:
            # Install all found modules and stop
            install_command = base_command + ["-i", f"base,{','.join(all_modules)}", "--save", "--stop-after-init"]
            print("Installing modules with command:", " ".join(install_command))
            subprocess.run(install_command, check=True)

        elif args.run_odoo:
            # Run Odoo server
            run_command = base_command
            print("Running Odoo server with command:", " ".join(run_command))
            subprocess.run(run_command, check=True)

        elif args.shell:
            # Open Odoo shell
            shell_command = base_command + ["shell"]
            print("Initializing Odoo shell with command:", " ".join(shell_command))
            subprocess.run(shell_command, check=True)

        elif args.update:
            # Update a specific module
            update_command = base_command + ["-u", args.update]
            print(f"Updating module {args.update} with command:", " ".join(update_command))
            subprocess.run(update_command, check=True)

    except subprocess.CalledProcessError as e:
        print("Error occurred while running Odoo command:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
