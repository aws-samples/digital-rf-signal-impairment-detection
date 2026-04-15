#!/usr/bin/env python3
"""
Extract signal payload from DIFI packets
"""

import sys
import numpy as np
from difi_utils.difi_data_packet_class import DifiDataPacket
from drx import process_data
import io

def extract_payload_from_bytes(data_bytes, context_packet=None):
    """Extract complex IQ samples from DIFI data packet bytes"""
    stream = io.BytesIO(data_bytes)
    
    # Use the official DIFI packet parser for validation and structure
    packet = DifiDataPacket(stream)
    
    # Get data item size from context packet if available
    data_item_size = 16  # Default to 8-bit
    if context_packet and hasattr(context_packet, 'data_packet_payload_format'):
        data_item_size = context_packet.data_packet_payload_format['data_item_size']
    
    # DIFI data packet structure (per README examples):
    # - Header (4 bytes): packet type, class ID, etc.
    # - Stream ID (4 bytes)
    # - Class ID info (8 bytes): OUI + ICC/PCC  
    # - Integer timestamp (4 bytes)
    # - Fractional timestamp (8 bytes)
    # - Payload (remaining bytes)
    payload_bytes = data_bytes[28:]  # Skip 28-byte header
    
    # Determine numpy dtype based on bit depth
    if data_item_size <= 8:
        dtype_str = '>i1'  # 8-bit signed, big-endian
    elif data_item_size <= 16:
        dtype_str = '>i2'  # 16-bit signed, big-endian
    else:
        dtype_str = '>i4'  # 32-bit signed, big-endian
    
    # Parse interleaved I/Q samples
    samples = np.frombuffer(payload_bytes, dtype=dtype_str)
    
    # Convert to complex (I + jQ) - DIFI uses complex cartesian
    if len(samples) % 2 == 0:
        i_samples = samples[0::2]
        q_samples = samples[1::2]
        return i_samples + 1j * q_samples
    
    return samples

def extract_payload_from_pcap(pcap_file, output_prefix="packet", max_packets=None):
    """Extract IQ samples from each UDP packet to separate files"""
    from scapy.all import PcapReader, UDP
    import os
    
    context_packet = None
    data_packet_count = 0
    
    for packet in PcapReader(pcap_file):
        if UDP in packet:
            try:
                payload_data = bytes(packet[UDP].payload)
                if len(payload_data) >= 8:
                    pkt_type = (int.from_bytes(payload_data[:4], 'big') >> 28) & 0x0f
                    
                    if pkt_type == 4:  # DIFI_STANDARD_FLOW_SIGNAL_CONTEXT
                        from difi_utils.difi_context_packet_class import DifiStandardContextPacket
                        context_packet = DifiStandardContextPacket(io.BytesIO(payload_data))
                    
                    elif pkt_type == 1:  # DIFI_STANDARD_FLOW_SIGNAL_DATA_WITH_STREAMID
                        if max_packets and data_packet_count >= max_packets:
                            break
                            
                        samples = extract_payload_from_bytes(payload_data, context_packet)
                        if samples is not None:
                            output_file = f"{output_prefix}_{data_packet_count:03d}.csv"
                            np.savetxt(output_file, np.column_stack([samples.real, samples.imag]), 
                                     delimiter=',', fmt='%.6f')
                            print(f"Saved {len(samples)} samples to {output_file}")
                            data_packet_count += 1
            except:
                continue
    
    print(f"Processed {data_packet_count} data packets")
    return data_packet_count

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract DIFI payload to separate files per UDP packet')
    parser.add_argument('pcap_file', help='Input PCAP file')
    parser.add_argument('--prefix', default='packet', help='Output file prefix (default: packet)')
    parser.add_argument('--max-packets', type=int, help='Maximum number of data packets to process')
    
    args = parser.parse_args()
    
    count = extract_payload_from_pcap(args.pcap_file, args.prefix, args.max_packets)
    if count == 0:
        print("No DIFI data packets found")