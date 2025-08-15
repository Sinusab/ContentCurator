from html import escape

def format_post_caption(post):
    """
    Format post information into a properly formatted Telegram message with HTML.
    The message includes the original post content and a blockquote footer.
    
    Args:
        post (dict): Post data containing text, channel, views, forwards, etc.
        
    Returns:
        str: Formatted HTML message ready for Telegram
    """
    # Escape HTML characters in the original text to prevent parsing issues
    original_text = escape(post.get('text', ''))
    
    # If the post has no text content, create a placeholder
    if not original_text.strip():
        original_text = "[Media post without text]"
    
    # Create the formatted message with HTML blockquote for the footer
    formatted_message = f"{original_text}\n\n<blockquote>powered by Sinus-Alpha</blockquote>"
    
    return formatted_message

def calculate_interaction_score(views, forwards, reactions=0):
    """
    Calculate interaction score for a post based on various metrics.
    
    Args:
        views (int): Number of views
        forwards (int): Number of forwards
        reactions (int): Number of reactions (optional)
        
    Returns:
        int: Calculated interaction score
    """
    # Weight forwards more heavily as they indicate higher engagement
    return views + (forwards * 2) + (reactions * 3)

def validate_post_data(post):
    """
    Validate that a post contains all required data fields.
    
    Args:
        post (dict): Post data to validate
        
    Returns:
        bool: True if post data is valid, False otherwise
    """
    required_fields = ['channel', 'id', 'text', 'views', 'forwards', 'has_media']
    return all(field in post for field in required_fields)
