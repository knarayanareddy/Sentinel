#!/usr/bin/env python3
"""
Test the text chunking logic in vector_store.py
"""
import sys
sys.path.insert(0, '/home/user/Sentinel')

from sentinel.vector_store import _chunk_text

def test_short_text():
    """Short text should not be chunked"""
    text = "This is a short text that fits in one chunk."
    chunks = _chunk_text(text, max_chunk_size=800)
    assert len(chunks) == 1, f"Expected 1 chunk, got {len(chunks)}"
    assert chunks[0] == text
    print("✓ Short text test passed")

def test_paragraph_splitting():
    """Text with paragraphs should be split intelligently"""
    # Create text with multiple paragraphs
    para1 = "First paragraph with some content. " * 10  # ~300 chars
    para2 = "Second paragraph with different content. " * 10  # ~350 chars
    para3 = "Third paragraph here. " * 10  # ~220 chars
    
    text = f"{para1}\n\n{para2}\n\n{para3}"
    
    chunks = _chunk_text(text, max_chunk_size=800)
    
    # Should split into multiple chunks since total is ~870 chars
    assert len(chunks) >= 2, f"Expected at least 2 chunks, got {len(chunks)}"
    
    # Each chunk should be <= 800 chars
    for i, chunk in enumerate(chunks):
        assert len(chunk) <= 800, f"Chunk {i} exceeds 800 chars: {len(chunk)}"
    
    # All content should be preserved (accounting for whitespace normalization)
    total_chars = sum(len(c) for c in chunks)
    # Allow some variance due to whitespace handling
    assert total_chars >= len(text) * 0.9, f"Lost too much content: {total_chars} vs {len(text)}"
    
    print(f"✓ Paragraph splitting test passed ({len(chunks)} chunks)")

def test_very_long_paragraph():
    """Single paragraph exceeding limit should be split by sentences"""
    # Create a very long single paragraph
    long_para = "This is sentence number {}. ".format
    text = "".join([long_para(i) for i in range(100)])  # ~2500 chars, one paragraph
    
    chunks = _chunk_text(text, max_chunk_size=800)
    
    # Should split into multiple chunks
    assert len(chunks) >= 3, f"Expected at least 3 chunks, got {len(chunks)}"
    
    # Each chunk should be <= 800 chars
    for i, chunk in enumerate(chunks):
        assert len(chunk) <= 800, f"Chunk {i} exceeds 800 chars: {len(chunk)}"
    
    print(f"✓ Very long paragraph test passed ({len(chunks)} chunks)")

def test_empty_and_whitespace():
    """Empty text and whitespace should be handled gracefully"""
    # Empty text
    chunks = _chunk_text("", max_chunk_size=800)
    assert len(chunks) == 0 or (len(chunks) == 1 and chunks[0] == "")
    
    # Only whitespace
    chunks = _chunk_text("\n\n\n   \n\n", max_chunk_size=800)
    assert len(chunks) == 0
    
    print("✓ Empty/whitespace test passed")

def test_real_document():
    """Test with actual demo corpus document"""
    with open('/home/user/Sentinel/docs/demo_corpus/credit_agreement.md', 'r') as f:
        text = f.read()
    
    print(f"Original document size: {len(text)} chars")
    
    chunks = _chunk_text(text, max_chunk_size=800)
    
    print(f"Split into {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks, 1):
        print(f"  Chunk {i}: {len(chunk)} chars - {chunk[:50]}...")
        assert len(chunk) <= 800, f"Chunk {i} exceeds 800 chars: {len(chunk)}"
    
    print("✓ Real document test passed")

if __name__ == "__main__":
    print("Testing text chunking logic...\n")
    
    test_short_text()
    test_paragraph_splitting()
    test_very_long_paragraph()
    test_empty_and_whitespace()
    test_real_document()
    
    print("\n✅ All chunking tests passed!")
