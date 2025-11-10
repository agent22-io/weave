#!/bin/bash
# Weave CLI Installation Script
# Usage: curl -fsSL https://weave.dev/install.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/weave/weave-cli.git"
INSTALL_DIR="${HOME}/.weave-cli"
PYTHON_MIN_VERSION="3.9"

# Print colored message
print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}┌────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│                                        │${NC}"
    echo -e "${BLUE}│  ${CYAN}🧵  Weave CLI Installation${BLUE}       │${NC}"
    echo -e "${BLUE}│                                        │${NC}"
    echo -e "${BLUE}└────────────────────────────────────────┘${NC}"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    print_info "Checking Python installation..."

    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        print_info "Please install Python ${PYTHON_MIN_VERSION} or higher"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_success "Found Python ${PYTHON_VERSION}"

    # Basic version check (comparing major.minor)
    MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 9 ]); then
        print_warning "Python ${PYTHON_VERSION} found, but ${PYTHON_MIN_VERSION}+ recommended"
    fi
}

# Check Git
check_git() {
    print_info "Checking Git installation..."

    if ! command_exists git; then
        print_error "Git is not installed"
        print_info "Please install Git first"
        exit 1
    fi

    print_success "Git is installed"
}

# Check pip
check_pip() {
    print_info "Checking pip installation..."

    if ! command_exists pip3 && ! python3 -m pip --version >/dev/null 2>&1; then
        print_error "pip is not installed"
        print_info "Please install pip first"
        exit 1
    fi

    print_success "pip is available"
}

# Install Weave
install_weave() {
    print_info "Installing Weave CLI..."

    # Create installation directory
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Installation directory exists: $INSTALL_DIR"
        read -p "Remove and reinstall? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            print_info "Updating existing installation..."
            cd "$INSTALL_DIR"
            git pull
            pip3 install -e . --quiet
            print_success "Updated Weave CLI"
            return
        fi
    fi

    # Clone repository
    print_info "Cloning repository..."
    git clone --quiet "$REPO_URL" "$INSTALL_DIR"
    print_success "Repository cloned"

    # Install package
    print_info "Installing package..."
    cd "$INSTALL_DIR"
    pip3 install -e . --quiet
    print_success "Weave CLI installed"
}

# Install optional features
install_optional() {
    echo ""
    print_info "Optional Features"
    echo ""

    read -p "Install LLM support (OpenAI, Anthropic)? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "Installing LLM support..."
        pip3 install -e ".[llm]" --quiet
        print_success "LLM support installed"
    fi

    read -p "Install deployment support (AWS, GCP, Docker)? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "Installing deployment support..."
        pip3 install -e ".[deploy]" --quiet
        print_success "Deployment support installed"
    fi

    read -p "Install development tools (auto-reload)? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        print_info "Installing development tools..."
        pip3 install -e ".[watch]" --quiet
        print_success "Development tools installed"
    fi
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."

    if command_exists weave; then
        VERSION=$(weave --version 2>&1 || echo "unknown")
        print_success "Weave CLI is installed: $VERSION"
    else
        print_warning "weave command not found in PATH"
        print_info "You may need to restart your shell or add to PATH"
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo -e "${GREEN}┌────────────────────────────────────────┐${NC}"
    echo -e "${GREEN}│  Installation Complete! 🎉            │${NC}"
    echo -e "${GREEN}└────────────────────────────────────────┘${NC}"
    echo ""
    print_info "Next Steps:"
    echo ""
    echo "  1. Verify installation:"
    echo -e "     ${CYAN}weave --version${NC}"
    echo ""
    echo "  2. Run setup wizard:"
    echo -e "     ${CYAN}weave setup${NC}"
    echo ""
    echo "  3. Install shell completion:"
    echo -e "     ${CYAN}weave completion bash --install${NC}"
    echo ""
    echo "  4. Create example project:"
    echo -e "     ${CYAN}weave init${NC}"
    echo ""
    echo "  5. Test with mock execution:"
    echo -e "     ${CYAN}weave apply${NC}"
    echo ""
    echo -e "${BLUE}📚 Documentation:${NC} https://docs.weave.dev"
    echo -e "${BLUE}💬 Community:${NC}     https://github.com/weave/weave-cli"
    echo ""
}

# Main installation flow
main() {
    print_header

    # Pre-flight checks
    check_python
    check_git
    check_pip

    echo ""

    # Install
    install_weave

    # Optional features
    install_optional

    echo ""

    # Verify
    verify_installation

    # Next steps
    show_next_steps
}

# Run main function
main
