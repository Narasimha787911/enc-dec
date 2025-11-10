import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from blockchain import Blockchain

def generate_benchmark_chart():
    blockchain = Blockchain()
    blocks = blockchain.get_all_blocks()
    
    if not blocks:
        return None
    
    data = {
        'AES-256-GCM': {'enc_times': [], 'dec_times': [], 'file_sizes': []},
        'Blowfish-256-EAX': {'enc_times': [], 'dec_times': [], 'file_sizes': []},
        'ChaCha20-Poly1305': {'enc_times': [], 'dec_times': [], 'file_sizes': []}
    }
    
    for block in blocks:
        algo = block['algorithm']
        if algo in data:
            data[algo]['enc_times'].append(block['enc_time_ms'])
            if block['dec_time_ms'] > 0:
                data[algo]['dec_times'].append(block['dec_time_ms'])
            data[algo]['file_sizes'].append(block['file_size_bytes'] / 1024)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Encryption Algorithm Performance Comparison', fontsize=16, fontweight='bold')
    
    algorithms = ['AES-256-GCM', 'Blowfish-256-EAX', 'ChaCha20-Poly1305']
    colors = ['#5B7FFF', '#8E5BFF', '#FF5BCD']
    
    avg_enc_times = []
    avg_dec_times = []
    avg_file_sizes = []
    
    for algo in algorithms:
        enc_times = data[algo]['enc_times']
        dec_times = data[algo]['dec_times']
        file_sizes = data[algo]['file_sizes']
        
        avg_enc_times.append(sum(enc_times) / len(enc_times) if enc_times else 0)
        avg_dec_times.append(sum(dec_times) / len(dec_times) if dec_times else 0)
        avg_file_sizes.append(sum(file_sizes) / len(file_sizes) if file_sizes else 0)
    
    axes[0, 0].bar(algorithms, avg_enc_times, color=colors, alpha=0.8)
    axes[0, 0].set_title('Average Encryption Time', fontweight='bold')
    axes[0, 0].set_ylabel('Time (ms)')
    axes[0, 0].grid(axis='y', alpha=0.3)
    for i, v in enumerate(avg_enc_times):
        axes[0, 0].text(i, v + max(avg_enc_times) * 0.02, f'{v:.2f}', ha='center', fontweight='bold')
    
    axes[0, 1].bar(algorithms, avg_dec_times, color=colors, alpha=0.8)
    axes[0, 1].set_title('Average Decryption Time', fontweight='bold')
    axes[0, 1].set_ylabel('Time (ms)')
    axes[0, 1].grid(axis='y', alpha=0.3)
    for i, v in enumerate(avg_dec_times):
        if v > 0:
            axes[0, 1].text(i, v + max(avg_dec_times) * 0.02, f'{v:.2f}', ha='center', fontweight='bold')
    
    axes[1, 0].bar(algorithms, avg_file_sizes, color=colors, alpha=0.8)
    axes[1, 0].set_title('Average File Size', fontweight='bold')
    axes[1, 0].set_ylabel('Size (KB)')
    axes[1, 0].grid(axis='y', alpha=0.3)
    for i, v in enumerate(avg_file_sizes):
        if v > 0:
            axes[1, 0].text(i, v + max(avg_file_sizes) * 0.02, f'{v:.2f}', ha='center', fontweight='bold')
    
    x = range(len(algorithms))
    width = 0.35
    x_enc = [i - width/2 for i in x]
    x_dec = [i + width/2 for i in x]
    
    axes[1, 1].bar(x_enc, avg_enc_times, width, label='Encryption', color=colors, alpha=0.8)
    axes[1, 1].bar(x_dec, avg_dec_times, width, label='Decryption', color=colors, alpha=0.5)
    axes[1, 1].set_title('Encryption vs Decryption Time', fontweight='bold')
    axes[1, 1].set_ylabel('Time (ms)')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(algorithms, rotation=15, ha='right')
    axes[1, 1].legend()
    axes[1, 1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    plt.close()
    
    return img_base64

def get_benchmark_stats():
    blockchain = Blockchain()
    blocks = blockchain.get_all_blocks()
    
    stats = {
        'AES-256-GCM': {'count': 0, 'avg_enc': 0, 'avg_dec': 0, 'avg_size': 0},
        'Blowfish-256-EAX': {'count': 0, 'avg_enc': 0, 'avg_dec': 0, 'avg_size': 0},
        'ChaCha20-Poly1305': {'count': 0, 'avg_enc': 0, 'avg_dec': 0, 'avg_size': 0}
    }
    
    for block in blocks:
        algo = block['algorithm']
        if algo in stats:
            stats[algo]['count'] += 1
            stats[algo]['avg_enc'] += block['enc_time_ms']
            stats[algo]['avg_dec'] += block['dec_time_ms']
            stats[algo]['avg_size'] += block['file_size_bytes'] / 1024
    
    for algo in stats:
        if stats[algo]['count'] > 0:
            stats[algo]['avg_enc'] /= stats[algo]['count']
            stats[algo]['avg_dec'] /= stats[algo]['count']
            stats[algo]['avg_size'] /= stats[algo]['count']
    
    return stats
