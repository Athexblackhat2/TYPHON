#!/bin/bash
# TYPHON DDoS - AUTO INSTALLATION SCRIPT v4.0
# Created by ATHEX BLACK HAT
# Fixed & Optimized for Cross-Platform Compatibility
# NOW WITH VERSION SELECTOR

set -e  # exit on error
set -o pipefail

# ============================================
# COLOR DEFINITIONS
# ============================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
ORANGE='\033[38;2;255;165;0m'
PINK='\033[38;2;255;20;147m'
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
BLINK='\033[5m'

# ============================================
# GLOBAL VARIABLES
# ============================================
OS="unknown"
PKG_MANAGER="unknown"
PYTHON_CMD="python3"
PIP_CMD="pip3"
VENV_DIR="athex"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SELECTED_VERSION="v3"
INSTALL_DIR="${SCRIPT_DIR}"

# ============================================
# UTILITY FUNCTIONS
# ============================================

spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while ps -p "$pid" >/dev/null 2>&1; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

countdown() {
    local seconds=$1
    for ((i=seconds; i>0; i--)); do
        echo -ne "${YELLOW} Starting in ${RED}$i${YELLOW} seconds...${RESET}\r"
        sleep 1
    done
    echo -ne "\r\033[K"
}

print_status() {
    echo -e "${CYAN}[*]${RESET} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${RESET} $1"
}

print_error() {
    echo -e "${RED}[✗]${RESET} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${RESET} $1"
}

print_info() {
    echo -e "${BLUE}[i]${RESET} $1"
}

# ============================================
# BANNER
# ============================================
show_banner() {
    clear
    echo -e "${PINK}"
    cat << "EOF"
         ████████╗██╗   ██╗██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗
         ╚══██╔══╝╚██╗ ██╔╝██╔══██╗██║  ██║██╔═══██╗████╗  ██║
            ██║    ╚████╔╝ ██████╔╝███████║██║   ██║██╔██╗ ██║
            ██║     ╚██╔╝  ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║
            ██║      ██║   ██║     ██║  ██║╚██████╔╝██║ ╚████║
            ╚═╝      ╚═╝   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
EOF
    echo -e "${RESET}"
    echo -e "${CYAN}   ⚡ AUTO INSTALLER v4.0 ⚡${RESET}\n"
    echo -e "${ORANGE}   Developed by ATHEX BLACK HAT${RESET}"
    echo -e "${PINK}$(printf '═%.0s' {1..60})${RESET}\n"
}

# ============================================
# VERSION SELECTOR
# ============================================
select_version() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗"
    echo -e "${CYAN}║  ${YELLOW}SELECT TYPHON VERSION${CYAN}                                         ║"
    echo -e "${CYAN}╠══════════════════════════════════════════════════════════╣"
    echo -e "${CYAN}║                                                          ║"
    echo -e "${CYAN}║  ${GREEN}[1]${RESET} TYPHON ${GREEN}v2.0${RESET} — Classic Edition                      ║"
    echo -e "${CYAN}║      ${DIM}• 25+ Attack Methods${RESET}                                         ║"
    echo -e "${CYAN}║      ${DIM}• Original Architecture${RESET}                                     ║"
    echo -e "${CYAN}║      ${DIM}• Stable & Proven${RESET}                                           ║"
    echo -e "${CYAN}║                                                          ║"
    echo -e "${CYAN}║  ${MAGENTA}[2]${RESET} TYPHON ${MAGENTA}v3.0${RESET} — Advanced Edition (${BLINK}RECOMMENDED${RESET})   ║"
    echo -e "${CYAN}║      ${DIM}• 30+ Attack Methods${RESET}                                         ║"
    echo -e "${CYAN}║      ${DIM}• HTTP/2 • Proxy Rotation • Amplification${RESET}                    ║"
    echo -e "${CYAN}║      ${DIM}• Special Attacks: SKY, STELLAR, TORNADO${RESET}                     ║"
    echo -e "${CYAN}║      ${DIM}• 2000+ Lines of Pure Power${RESET}                                 ║"
    echo -e "${CYAN}║                                                          ║"
    echo -e "${CYAN}║  ${YELLOW}[3]${RESET} TYPHON ${YELLOW}v4.0${RESET} — Ultimate Edition (${BLINK}NEW${RESET})            ║"
    echo -e "${CYAN}║      ${DIM}• 40+ Attack Methods${RESET}                                         ║"
    echo -e "${CYAN}║      ${DIM}• All v3 Features + More${RESET}                                    ║"
    echo -e "${CYAN}║      ${DIM}• Enterprise Grade Performance${RESET}                              ║"
    echo -e "${CYAN}║      ${DIM}• Future Updates Included${RESET}                                   ║"
    echo -e "${CYAN}║                                                          ║"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${RESET}"
    echo
    
    while true; do
        read -rp "Enter your choice [1-3]: " choice
        case $choice in
            1)
                SELECTED_VERSION="v2"
                print_info "Selected: TYPHON v2.0 — Classic Edition"
                break
                ;;
            2)
                SELECTED_VERSION="v3"
                print_info "Selected: TYPHON v3.0 — Advanced Edition"
                break
                ;;
            3)
                SELECTED_VERSION="v4"
                print_info "Selected: TYPHON v4.0 — Ultimate Edition"
                break
                ;;
            *)
                print_error "Invalid choice. Please enter 1, 2, or 3."
                ;;
        esac
    done
    
    sleep 1
}

# ============================================
# INSTALL VERSION SPECIFIC FILES
# ============================================
install_version_files() {
    print_status "Installing TYPHON ${SELECTED_VERSION} files..."
    
    case $SELECTED_VERSION in
        v2)
            # Check if v2 main.py exists, if not create it
            if [ ! -f "main_v2.py" ] && [ ! -f "main.py" ]; then
                print_warning "main_v2.py not found. Creating default v2 file..."
                cp main.py main_v2.py 2>/dev/null || {
                    print_error "No main.py found to copy. Please provide main_v2.py"
                    exit 1
                }
            fi
            # Ensure main.py points to v2
            if [ -f "main_v2.py" ]; then
                cp main_v2.py main.py
                print_success "TYPHON v2.0 installed as main.py"
            else
                print_success "TYPHON v2.0 ready (using existing main.py)"
            fi
            ;;
        v3)
            # Check if v3 file exists
            if [ -f "typhon_v3.py" ]; then
                cp typhon_v3.py main.py
                print_success "TYPHON v3.0 installed as main.py"
            elif [ -f "main_v3.py" ]; then
                cp main_v3.py main.py
                print_success "TYPHON v3.0 installed as main.py"
            else
                print_warning "typhon_v3.py not found. Checking for existing main.py..."
                if [ -f "main.py" ]; then
                    print_warning "Using existing main.py as v3"
                else
                    print_error "No v3 file found! Creating default..."
                    cat > main.py << 'EOFV3'
#!/usr/bin/env python3
# TYPHON v3.0 - Advanced DDoS Toolkit
# Placeholder - Please replace with actual v3 code
print("TYPHON v3.0 - Advanced Edition")
print("Please install the full v3 code from the repository.")
EOFV3
                    print_success "Created placeholder main.py for v3"
                fi
            fi
            ;;
        v4)
            # Check if v4 file exists
            if [ -f "typhon_v4.py" ]; then
                cp typhon_v4.py main.py
                print_success "TYPHON v4.0 installed as main.py"
            elif [ -f "main_v4.py" ]; then
                cp main_v4.py main.py
                print_success "TYPHON v4.0 installed as main.py"
            else
                print_warning "typhon_v4.py not found. Installing from repository..."
                # Download latest v4 from GitHub or create default
                if command -v wget &>/dev/null; then
                    wget -O main.py https://raw.githubusercontent.com/Athexblackhat/TYPHON/main/typhon_v4.py 2>/dev/null || {
                        print_warning "Download failed. Using existing main.py"
                    }
                elif command -v curl &>/dev/null; then
                    curl -o main.py https://raw.githubusercontent.com/Athexblackhat/TYPHON/main/typhon_v4.py 2>/dev/null || {
                        print_warning "Download failed. Using existing main.py"
                    }
                fi
                
                if [ ! -f "main.py" ]; then
                    print_error "No v4 file found! Creating default..."
                    cat > main.py << 'EOFV4'
#!/usr/bin/env python3
# TYPHON v4.0 - Ultimate DDoS Toolkit
# Placeholder - Please replace with actual v4 code
print("TYPHON v4.0 - Ultimate Edition")
print("Please install the full v4 code from the repository.")
EOFV4
                    print_success "Created placeholder main.py for v4"
                else
                    print_success "TYPHON v4.0 installed as main.py"
                fi
            fi
            ;;
    esac
    
    # Create version info file
    echo "${SELECTED_VERSION}" > .typhon_version
    print_success "Version info saved"
}

# ============================================
# SYSTEM DETECTION
# ============================================
detect_os() {
    print_status "Detecting Operating System..."
    sleep 0.5

    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "linux"* ]]; then
        OS="linux"
        if command -v apt &>/dev/null; then
            PKG_MANAGER="apt"
            print_success "Debian/Ubuntu detected (apt)"
        elif command -v yum &>/dev/null; then
            PKG_MANAGER="yum"
            print_success "RHEL/CentOS detected (yum)"
        elif command -v dnf &>/dev/null; then
            PKG_MANAGER="dnf"
            print_success "Fedora detected (dnf)"
        elif command -v pacman &>/dev/null; then
            PKG_MANAGER="pacman"
            print_success "Arch detected (pacman)"
        elif command -v pkg &>/dev/null; then
            PKG_MANAGER="pkg"
            print_success "Termux detected (pkg)"
        else
            print_error "Unknown package manager"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        if command -v brew &>/dev/null; then
            PKG_MANAGER="brew"
            print_success "macOS detected (homebrew)"
        else
            print_warning "Homebrew not found"
            print_status "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            PKG_MANAGER="brew"
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
        print_warning "Windows detected - limited support"
        print_status "Please install Python manually from python.org"
        print_status "Then run: pip install -r requirements.txt"
        exit 0
    else
        print_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# ============================================
# INSTALL PACKAGES
# ============================================
install_packages() {
    print_status "Installing system dependencies..."

    case $PKG_MANAGER in
        apt)
            sudo apt-get update -qq
            sudo apt-get install -y -qq python3 python3-pip python3-venv git wget curl bc unzip
            ;;
        yum)
            sudo yum install -y -q python3 python3-pip git wget curl bc unzip
            ;;
        dnf)
            sudo dnf install -y -q python3 python3-pip git wget curl bc unzip
            ;;
        pacman)
            sudo pacman -S --noconfirm python python-pip git wget curl bc unzip
            ;;
        pkg)
            pkg install -y python python-pip git wget curl bc unzip
            ;;
        brew)
            brew install python3 git wget curl bc unzip
            ;;
        *)
            print_error "Unsupported package manager: $PKG_MANAGER"
            exit 1
            ;;
    esac

    print_success "System dependencies installed"
}

# ============================================
# CHECK PYTHON
# ============================================
check_python() {
    print_status "Checking Python installation..."

    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif command -v python &>/dev/null; then
        PYTHON_CMD="python"
        PIP_CMD="pip"
    else
        print_error "Python not found!"
        print_status "Installing Python..."
        case $PKG_MANAGER in
            apt) sudo apt-get install -y python3 python3-pip ;;
            yum) sudo yum install -y python3 python3-pip ;;
            dnf) sudo dnf install -y python3 python3-pip ;;
            pacman) sudo pacman -S --noconfirm python python-pip ;;
            pkg) pkg install -y python python-pip ;;
            brew) brew install python3 ;;
        esac
    fi

    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    print_success "Python: $PYTHON_VERSION"
}

# ============================================
# SETUP VIRTUAL ENVIRONMENT
# ============================================
setup_venv() {
    print_status "Setting up virtual environment..."

    cd "$SCRIPT_DIR"

    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment '$VENV_DIR' already exists"
        read -rp "Recreate? (y/n): " recreate
        if [[ $recreate =~ ^[Yy]$ ]]; then
            print_status "Removing existing environment..."
            rm -rf "$VENV_DIR"
        else
            print_success "Using existing environment"
            source "$VENV_DIR/bin/activate" 2>/dev/null || {
                print_error "Failed to activate existing environment"
                print_status "Removing and recreating..."
                rm -rf "$VENV_DIR"
                print_status "Creating fresh environment..."
                $PYTHON_CMD -m venv "$VENV_DIR"
                source "$VENV_DIR/bin/activate"
            }
            return 0
        fi
    fi

    print_status "Creating virtual environment '$VENV_DIR'..."
    $PYTHON_CMD -m venv "$VENV_DIR" 2>/dev/null || {
        print_warning "venv module not found, installing virtualenv..."
        $PIP_CMD install virtualenv
        virtualenv "$VENV_DIR"
    }

    print_success "Virtual environment created"

    # Activate
    print_status "Activating virtual environment..."
    source "$VENV_DIR/bin/activate" 2>/dev/null || {
        print_error "Failed to activate virtual environment"
        exit 1
    }

    print_success "Virtual environment activated"

    # Show info
    echo
    print_success "Virtual Environment Info:"
    echo -e "${CYAN}   • Name:${RESET} ${PINK}$VENV_DIR${RESET}"
    echo -e "${CYAN}   • Python:${RESET} $(which python3 2>/dev/null || which python)"
    echo -e "${CYAN}   • Version:${RESET} $($PYTHON_CMD --version 2>&1)"
    echo -e "${CYAN}   • Path:${RESET} $(pwd)/$VENV_DIR"
    echo
}

# ============================================
# INSTALL REQUIREMENTS
# ============================================
install_requirements() {
    print_status "Installing Python packages..."

    # Upgrade pip
    print_status "Upgrading pip..."
    $PIP_CMD install --upgrade pip -q

    # Check if requirements.txt exists
    if [ ! -f "requirements.txt" ]; then
        print_warning "requirements.txt not found"
        print_status "Creating requirements.txt..."
        cat > requirements.txt << 'EOF'
cloudscraper>=1.2.60
pysocks>=1.7.1
colorama>=0.4.6
httpx>=0.24.0
requests>=2.28.0
urllib3>=1.26.0
certifi>=2023.0.0
chardet>=5.0.0
idna>=3.0.0
cryptography>=39.0.0
pyOpenSSL>=23.0.0
aiohttp>=3.8.0
aiodns>=3.0.0
brotli>=1.0.0
h2>=4.0.0
websockets>=11.0.0
fake-useragent>=1.4.0
psutil>=5.9.0
setuptools>=65.0.0
wheel>=0.38.0
undetected-chromedriver>=3.1.0
selenium>=4.0.0
dataclasses
typing-extensions
EOF
        print_success "requirements.txt created"
    fi

    # Install wheel and setuptools first
    print_status "Installing build tools..."
    $PIP_CMD install wheel setuptools -q

    # Install requirements with progress
    print_status "Installing packages (this may take a few minutes)..."

    # Count packages
    TOTAL=$(grep -v '^#' requirements.txt | grep -v '^$' | wc -l)
    CURRENT=0
    FAILED=0

    while IFS= read -r package || [ -n "$package" ]; do
        if [[ $package =~ ^#.* ]] || [[ -z $package ]]; then
            continue
        fi

        CURRENT=$((CURRENT + 1))
        PACKAGE_NAME=$(echo "$package" | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | xargs)

        echo -ne "${CYAN}[${CURRENT}/${TOTAL}] Installing ${ORANGE}$PACKAGE_NAME${RESET}... "

        if $PIP_CMD install "$package" -q 2>/dev/null; then
            echo -e "${GREEN}✓${RESET}"
        else
            echo -e "${RED}✗${RESET}"
            FAILED=1
        fi
    done < requirements.txt

    if [ $FAILED -eq 0 ]; then
        print_success "All packages installed successfully!"
    else
        print_warning "Some packages failed to install"
        print_status "Try: pip install -r requirements.txt"
    fi

    echo
}

# ============================================
# CREATE HELPER SCRIPTS
# ============================================
create_helpers() {
    print_status "Creating helper scripts..."

    # Activate script
    cat > activate.sh << 'EOF'
#!/bin/bash
source athex/bin/activate
echo -e "\033[0;32m✓ Virtual environment 'athex' activated!\033[0m"
echo -e "\033[0;36m💡 Type 'deactivate' to exit\033[0m"
EOF
    chmod +x activate.sh

    # Run script
    cat > run.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source athex/bin/activate
python3 main.py "$@"
EOF
    chmod +x run.sh

    # Version switcher script
    cat > switch_version.sh << 'EOF'
#!/bin/bash
# TYPHON Version Switcher

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
PINK='\033[38;2;255;20;147m'
RESET='\033[0m'
BOLD='\033[1m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗"
echo -e "${CYAN}║  ${YELLOW}TYPHON VERSION SWITCHER${CYAN}                                        ║"
echo -e "${CYAN}╠══════════════════════════════════════════════════════════╣"
echo -e "${CYAN}║                                                          ║"
echo -e "${CYAN}║  ${GREEN}[1]${RESET} Switch to TYPHON ${GREEN}v2.0${RESET} — Classic Edition              ║"
echo -e "${CYAN}║  ${MAGENTA}[2]${RESET} Switch to TYPHON ${MAGENTA}v3.0${RESET} — Advanced Edition         ║"
echo -e "${CYAN}║  ${YELLOW}[3]${RESET} Switch to TYPHON ${YELLOW}v4.0${RESET} — Ultimate Edition          ║"
echo -e "${CYAN}║                                                          ║"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${RESET}"
echo

read -rp "Select version [1-3]: " choice

case $choice in
    1)
        if [ -f "main_v2.py" ]; then
            cp main_v2.py main.py
            echo -e "${GREEN}✓ Switched to TYPHON v2.0${RESET}"
        else
            echo -e "${RED}✗ main_v2.py not found${RESET}"
        fi
        ;;
    2)
        if [ -f "typhon_v3.py" ]; then
            cp typhon_v3.py main.py
            echo -e "${GREEN}✓ Switched to TYPHON v3.0${RESET}"
        elif [ -f "main_v3.py" ]; then
            cp main_v3.py main.py
            echo -e "${GREEN}✓ Switched to TYPHON v3.0${RESET}"
        else
            echo -e "${RED}✗ v3 file not found${RESET}"
        fi
        ;;
    3)
        if [ -f "typhon_v4.py" ]; then
            cp typhon_v4.py main.py
            echo -e "${GREEN}✓ Switched to TYPHON v4.0${RESET}"
        elif [ -f "main_v4.py" ]; then
            cp main_v4.py main.py
            echo -e "${GREEN}✓ Switched to TYPHON v4.0${RESET}"
        else
            echo -e "${RED}✗ v4 file not found${RESET}"
        fi
        ;;
    *)
        echo -e "${RED}Invalid choice${RESET}"
        exit 1
        ;;
esac

echo -e "${CYAN}Current version: $(head -n1 main.py 2>/dev/null | grep -o 'v[0-9]\.[0-9]' || echo 'unknown')${RESET}"
EOF
    chmod +x switch_version.sh

    print_success "activate.sh created"
    print_success "run.sh created"
    print_success "switch_version.sh created"
}

# ============================================
# FINAL OUTPUT
# ============================================
show_completion() {
    clear
    echo -e "${PINK}"
    cat << "EOF"

     ████████╗██╗   ██╗██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗
     ╚══██╔══╝╚██╗ ██╔╝██╔══██╗██║  ██║██╔═══██╗████╗  ██║
        ██║    ╚████╔╝ ██████╔╝███████║██║   ██║██╔██╗ ██║
        ██║     ╚██╔╝  ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║
        ██║      ██║   ██║     ██║  ██║╚██████╔╝██║ ╚████║
        ╚═╝      ╚═╝   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
EOF
    echo -e "${RESET}\n"

    echo -e "${GREEN}${BOLD}✓ INSTALLATION COMPLETE!${RESET}\n"

    echo -e "${CYAN}📋 Quick Start Guide:${RESET}\n"
    echo -e "${YELLOW}  Method 1 - Quick Run:${RESET}"
    echo -e "${PINK}    ./run.sh${RESET}\n"
    echo -e "${YELLOW}  Method 2 - Manual Activation:${RESET}"
    echo -e "${PINK}    source activate.sh${RESET}"
    echo -e "${PINK}    python3 main.py${RESET}\n"
    echo -e "${YELLOW}  Method 3 - Direct:${RESET}"
    echo -e "${PINK}    source athex/bin/activate${RESET}"
    echo -e "${PINK}    python3 main.py${RESET}\n"

    echo -e "${MAGENTA}🔄 Switch Version:${RESET}"
    echo -e "${PINK}    ./switch_version.sh${RESET}\n"

    echo -e "${ORANGE}📌 Important Notes:${RESET}"
    echo -e "${CYAN}  • Current version: ${PINK}${SELECTED_VERSION}${RESET}"
    echo -e "${CYAN}  • To deactivate: ${PINK}deactivate${RESET}"
    echo -e "${CYAN}  • Virtual environment: ${PINK}$(pwd)/$VENV_DIR${RESET}"
    echo -e "${CYAN}  • For updates: ${PINK}./install.sh${RESET}\n"

    echo -e "${PINK}$(printf '═%.0s' {1..50})${RESET}"
    echo -e "${ORANGE}  Developed by ATHEX BLACK HAT${RESET}"
    echo -e "${PINK}$(printf '═%.0s' {1..50})${RESET}\n"

    print_success "TYPHON ${SELECTED_VERSION} is ready to use!"
}

# ============================================
# ERROR HANDLING
# ============================================
handle_error() {
    echo
    print_error "INSTALLATION FAILED!"
    print_warning "Check the error messages above"
    print_status "You can try: ./install.sh --force"
    exit 1
}

# ============================================
# MAIN
# ============================================
main() {
    trap 'handle_error' ERR

    # Parse arguments
    if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
        echo "Usage: ./install.sh [OPTIONS]"
        echo "  --help, -h    Show this help"
        echo "  --force       Force reinstall"
        echo "  --version     Specify version: v2, v3, or v4"
        exit 0
    fi

    # Check if version specified via argument
    if [[ "$1" == "--version" ]] && [[ -n "$2" ]]; then
        case $2 in
            v2|V2|2) SELECTED_VERSION="v2" ;;
            v3|V3|3) SELECTED_VERSION="v3" ;;
            v4|V4|4) SELECTED_VERSION="v4" ;;
            *) SELECTED_VERSION="v3" ;;
        esac
        print_info "Version specified: ${SELECTED_VERSION}"
    else
        show_banner
        select_version
    fi

    show_banner
    print_status "Starting TYPHON ${SELECTED_VERSION} installation..."

    detect_os
    install_packages
    check_python
    setup_venv
    install_requirements
    install_version_files
    create_helpers

    show_completion

    # Deactivate virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        deactivate 2>/dev/null || true
    fi

    print_success "Installation complete!"
}

# ============================================
# RUN
# ============================================
main "$@"
exit 0