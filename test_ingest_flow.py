#!/usr/bin/env python3
"""
Test the full ingest flow with chunking against the Vultr API
"""
import sys
import os
sys.path.insert(0, '/home/user/Sentinel')

from sentinel.vector_store import init_collection, ingest, search, set_collection_id

def test_full_ingest_flow():
    """Test ingesting all three demo corpus documents with chunking"""
    
    print("=" * 70)
    print("Testing Full Ingest Flow with Chunking")
    print("=" * 70)
    
    # Initialize a fresh collection for testing
    print("\n1. Creating fresh test collection...")
    collection_name = "sentinel-chunking-test"
    try:
        collection_id = init_collection(collection_name)
        print(f"✓ Collection created: {collection_id}")
    except Exception as e:
        print(f"✗ Failed to create collection: {e}")
        return False
    
    # Ingest all three demo corpus documents
    corpus_files = [
        '/home/user/Sentinel/docs/demo_corpus/credit_agreement.md',
        '/home/user/Sentinel/docs/demo_corpus/historical_ratios.md',
        '/home/user/Sentinel/docs/demo_corpus/recent_transactions.md'
    ]
    
    total_chunks = 0
    print(f"\n2. Ingesting {len(corpus_files)} documents...")
    
    for filepath in corpus_files:
        filename = os.path.basename(filepath)
        print(f"\n  Processing: {filename}")
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        print(f"  Original size: {len(content)} chars")
        
        try:
            item_ids = ingest(content, filename)
            total_chunks += len(item_ids)
            print(f"  ✓ Ingested {len(item_ids)} chunks")
        except Exception as e:
            print(f"  ✗ Failed to ingest: {e}")
            return False
    
    print(f"\n3. Total chunks ingested: {total_chunks}")
    
    # Test search to verify chunks are searchable
    print(f"\n4. Testing search functionality...")
    test_queries = [
        "Debt to EBITDA covenant threshold",
        "historical ratio trend",
        "recent transaction anomalies"
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        try:
            results = search(query, top_k=2)
            if results:
                print(f"  ✓ Found {len(results)} results")
                print(f"    Top result: {results[0].description}")
                print(f"    Content preview: {results[0].content[:100]}...")
            else:
                print(f"  ✗ No results found")
                return False
        except Exception as e:
            print(f"  ✗ Search failed: {e}")
            return False
    
    print("\n" + "=" * 70)
    print("✅ Full ingest flow test passed!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = test_full_ingest_flow()
    sys.exit(0 if success else 1)
