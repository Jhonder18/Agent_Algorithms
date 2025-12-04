from IPython.display import Image, display
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from io import BytesIO
from app.agents.graph import build_graph


try:
    # Get the mermaid PNG as bytes
    graph = build_graph().compile()
    png_bytes = graph.get_graph().draw_mermaid_png()
    
    # Try IPython display first (for Jupyter notebooks)

    # Fallback to matplotlib for other environments
    img = mpimg.imread(BytesIO(png_bytes), format='PNG')
    plt.figure(figsize=(12, 8))
    plt.imshow(img)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
        
except Exception as e:
    print(f"Could not display graph: {e}")
    # This requires some extra dependencies and is optional
    pass