import { marked } from 'marked';
import DOMPurify from 'dompurify';

const form = document.getElementById('chat-form');
const input = document.getElementById('user-input');
const chatHistory = document.getElementById('chat-history');

// Assuming backend runs on localhost:8000 locally
const API_URL = 'http://localhost:8000/api/chat';

function addMessage(text, sender, isHtml = false, sources = []) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}`;
  
  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = sender === 'user' ? 'YOU' : 'SYS';
  
  const content = document.createElement('div');
  content.className = 'message-content';
  
  if (isHtml) {
    content.innerHTML = text;
  } else {
    content.textContent = text;
  }

  // Append sources if available
  if (sources && sources.length > 0) {
    const sourcesDiv = document.createElement('div');
    sourcesDiv.className = 'sources-list';
    sourcesDiv.innerHTML = '<strong>Sources:</strong><br>';
    
    // Deduplicate sources by page number for cleaner UI
    const seenPages = new Set();
    sources.forEach(src => {
      const page = src.metadata.page;
      if (page !== undefined && !seenPages.has(page)) {
        seenPages.add(page);
        const srcBadge = document.createElement('span');
        srcBadge.className = 'source-item';
        srcBadge.textContent = `Page ${page}`;
        // Optionally add tooltip with snippet: srcBadge.title = src.page_content.substring(0, 100) + '...';
        sourcesDiv.appendChild(srcBadge);
      }
    });

    if (seenPages.size > 0) {
      content.appendChild(sourcesDiv);
    }
  }

  msgDiv.appendChild(avatar);
  msgDiv.appendChild(content);
  chatHistory.appendChild(msgDiv);
  
  // Scroll to bottom
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function addLoader() {
  const loaderDiv = document.createElement('div');
  loaderDiv.className = 'message system loader-msg';
  loaderDiv.innerHTML = `
    <div class="avatar">SYS</div>
    <div class="message-content">
      <div class="loader">
        <span></span><span></span><span></span>
      </div>
    </div>
  `;
  chatHistory.appendChild(loaderDiv);
  chatHistory.scrollTop = chatHistory.scrollHeight;
  return loaderDiv;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const query = input.value.trim();
  if (!query) return;
  
  // Add user message
  addMessage(query, 'user');
  input.value = '';
  
  // Add loading indicator
  const loader = addLoader();
  
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    });
    
    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Remove loader
    loader.remove();
    
    // Render model Markdown defensively before injecting it into the DOM.
    const htmlContent = DOMPurify.sanitize(marked.parse(data.answer));
    
    // Add system response
    addMessage(htmlContent, 'system', true, data.sources);
    
  } catch (error) {
    loader.remove();
    addMessage(`Error: Could not connect to RAG backend. Make sure the FastAPI server is running on localhost:8000.\n\nDetails: ${error.message}`, 'system');
  }
});
