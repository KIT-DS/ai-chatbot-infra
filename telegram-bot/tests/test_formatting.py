#!/usr/bin/env python3
"""
Test script to verify message formatting
Tests all message types without actually sending to Telegram
"""

import json
import re

# Sample responses from n8n
SAMPLE_RESPONSES = [
    {
        "name": "Simple answer",
        "response": "The Q1 budget is $50,000 for marketing department.",
        "sources": ["budget-q1-2025.pdf"]
    },
    {
        "name": "Answer with multiple sources",
        "response": "According to the latest financial reports, the Q1 budget allocation is as follows:\n\n• Marketing: $50,000\n• Sales: $30,000\n• Operations: $20,000\n\nTotal Q1 budget: $100,000",
        "sources": ["budget-q1-2025.pdf", "financial-report-jan-2025.xlsx"]
    },
    {
        "name": "Legal answer",
        "response": "The standard employment contract template can be found in the HR documents repository. Key sections include:\n\n1. Employee information\n2. Job title and responsibilities\n3. Compensation and benefits\n4. Termination clauses\n\nPlease review with legal department before using.",
        "sources": ["hr-contracts-template.docx", "legal-guidelines.pdf"]
    },
    {
        "name": "Project management answer",
        "response": "Current project deadlines:\n\n• Project Alpha: March 15, 2025\n• Project Beta: April 1, 2025\n• Project Gamma: May 30, 2025\n\nAll projects are on track according to the latest status report.",
        "sources": ["project-timeline-q1.pdf"]
    },
    {
        "name": "Long answer (test splitting)",
        "response": "Budget breakdown for Q1 2025:\n\n" + ("This is a long paragraph about budget details. " * 100),
        "sources": ["budget-detailed-2025.pdf"]
    }
]


def format_response(response_text: str) -> str:
    """Simulate the _format_response function"""
    # Clean up extra whitespace
    response_text = re.sub(r'\n{3,}', '\n\n', response_text)
    
    # Format sources section
    if '📚 Sources:' in response_text or '⚖️ Legal Sources:' in response_text or '📋 Project Sources:' in response_text:
        response_text = re.sub(
            r'(\n\n)(📚|⚖️|📋) (Sources|Legal Sources|Project Sources):',
            r'\n\n━━━━━━━━━━━━━━━\n\2 \3:',
            response_text
        )
    
    # Make source filenames bold
    response_text = re.sub(
        r'([\w\-]+\.(pdf|docx|txt|xlsx|csv))',
        r'*\1*',
        response_text
    )
    
    return response_text.strip()


def add_sources(text: str, sources: list) -> str:
    """Add sources section to response"""
    if sources:
        sources_text = ", ".join(sources)
        return f"{text}\n\n📚 Sources: {sources_text}"
    return text


def test_formatting():
    print("=" * 80)
    print("MESSAGE FORMATTING TEST")
    print("=" * 80)
    print()
    
    for i, sample in enumerate(SAMPLE_RESPONSES, 1):
        print(f"\n{'─' * 80}")
        print(f"TEST {i}: {sample['name']}")
        print(f"{'─' * 80}")
        
        # Add sources
        text_with_sources = add_sources(sample['response'], sample['sources'])
        
        # Format
        formatted = format_response(text_with_sources)
        
        # Check length
        length = len(formatted)
        chunks_needed = (length // 4096) + 1 if length > 4096 else 1
        
        print(f"\n📊 Stats:")
        print(f"  Length: {length} characters")
        print(f"  Chunks needed: {chunks_needed}")
        print(f"\n📝 Formatted output:\n")
        print(formatted)
        print()


def test_user_list():
    print("\n" + "=" * 80)
    print("USER LIST TEST")
    print("=" * 80)
    print()
    
    # Simulate list_all_users output
    users = ["kirun13", "john_doe", "jane_smith"]
    admins = ["kirun13", "jane_smith"]
    
    lines = ["📋 *Authorized Users:*\n"]
    for username in sorted(users):
        role = "👑 Admin" if username in admins else "👤 User"
        lines.append(f"  • @{username} — {role}\n")
    
    result = "".join(lines)
    print(result)


def test_command_messages():
    print("\n" + "=" * 80)
    print("COMMAND MESSAGES TEST")
    print("=" * 80)
    
    messages = {
        "/start (user)": """👋 *Welcome to the Corporate RAG Assistant!*

Send me a question and I'll find the answer from our internal documents.

📝 *Available commands:*
• /help — Show available commands
""",
        "/start (admin)": """👋 *Welcome to the Corporate RAG Assistant!*

Send me a question and I'll find the answer from our internal documents.

📝 *Available commands:*
• /help — Show available commands

👑 *Admin commands:*
• /adduser @username — Authorize a user
• /removeuser @username — Remove a user
• /addadmin @username — Promote to admin
• /removeadmin @username — Demote admin
• /listusers — Show all users

📎 Upload a document (PDF, DOCX, TXT, XLSX, CSV) to ingest it.""",
        "Query processing": """🔍 *Processing your query...*

I'm searching through our documents and will reply shortly.""",
        "Service unavailable": """⚠️ *Service Unavailable*

Could not reach the AI service. Please try again in a moment.

_If the problem persists, contact your administrator._""",
        "Document uploaded": """📄 *Document:* budget-report-q1.pdf

✅ Extracted *12,345* characters.

*Select the target namespace:*""",
        "Document processing": """⏳ *Processing Document*

📄 *File:* budget-report-q1.pdf
📁 *Namespace:* `finance`

Document sent for ingestion. You'll be notified when it's done.""",
        "Document ingested": """✅ *Document ingested: 15 chunks stored in 'finance' namespace.*

📄 Source: *budget-report-q1.pdf*"""
    }
    
    for title, msg in messages.items():
        print(f"\n{'─' * 80}")
        print(f"📬 {title}")
        print(f"{'─' * 80}")
        print(msg)
        print()


def test_error_messages():
    print("\n" + "=" * 80)
    print("ERROR MESSAGES TEST")
    print("=" * 80)
    
    errors = {
        "Unsupported format": """⚠️ *Unsupported file format:* `.exe`

*Allowed formats:* .csv, .docx, .pdf, .txt, .xlsx""",
        "Session expired": """⚠️ Session expired. Please upload the file again.""",
        "Unexpected error": """⚠️ *Unexpected Error*

An unexpected error occurred. Please try again later.

_If the problem persists, contact your administrator._"""
    }
    
    for title, msg in errors.items():
        print(f"\n{'─' * 80}")
        print(f"❌ {title}")
        print(f"{'─' * 80}")
        print(msg)
        print()


def main():
    print("\n" + "🧪 BOT MESSAGE FORMATTING TEST SUITE")
    print()
    
    test_formatting()
    test_user_list()
    test_command_messages()
    test_error_messages()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
    print()
    print("Visual inspection:")
    print("  ✓ Check for proper line breaks")
    print("  ✓ Check for Markdown formatting (*bold*, _italic_)")
    print("  ✓ Check for emoji alignment")
    print("  ✓ Check for message length limits")
    print()


if __name__ == "__main__":
    main()
