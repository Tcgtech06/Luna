import { useState, useRef, useEffect } from 'react'
import './App.css'
import axios from 'axios'

// Configure axios base URL - Your Hugging Face Space
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://tcgtech-luna-chatbot.hf.space'

// Icon components (replacing lucide-react)
const MoonIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
  </svg>
)

const SunIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="5"></circle>
    <line x1="12" y1="1" x2="12" y2="3"></line>
    <line x1="12" y1="21" x2="12" y2="23"></line>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
    <line x1="1" y1="12" x2="3" y2="12"></line>
    <line x1="21" y1="12" x2="23" y2="12"></line>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
  </svg>
)

const PaperclipIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
  </svg>
)

const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="22" y1="2" x2="11" y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
  </svg>
)

const ImageIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
    <circle cx="8.5" cy="8.5" r="1.5"></circle>
    <polyline points="21 15 16 10 5 21"></polyline>
  </svg>
)

const FileTextIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
    <polyline points="14 2 14 8 20 8"></polyline>
    <line x1="16" y1="13" x2="8" y2="13"></line>
    <line x1="16" y1="17" x2="8" y2="17"></line>
    <polyline points="10 9 9 9 8 9"></polyline>
  </svg>
)

const XIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
)

function App() {
  const [theme, setTheme] = useState('dark')
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [showUploadMenu, setShowUploadMenu] = useState(false)
  const chatContainerRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages, isTyping])

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files)
    const fileNames = files.map(f => f.name)
    setUploadedFiles([...uploadedFiles, ...fileNames])
    setShowUploadMenu(false)
  }

  const removeFile = (index) => {
    setUploadedFiles(uploadedFiles.filter((_, i) => i !== index))
  }

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      role: 'user',
      content: inputMessage,
      files: uploadedFiles
    }

    setMessages([...messages, userMessage])
    setInputMessage('')
    setIsTyping(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: inputMessage,
        files: uploadedFiles
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response
      }

      setMessages(prev => [...prev, assistantMessage])
      setUploadedFiles([])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, an error occurred. Please try again.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className={`app ${theme}`}>
      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="header-left">
            <div className="logo">🌙</div>
            <div className="header-title">
              <h1>Luna</h1>
              <p>Powered by TCG TECH</p>
            </div>
          </div>
          <button className="theme-toggle" onClick={toggleTheme}>
            {theme === 'dark' ? <MoonIcon /> : <SunIcon />}
          </button>
        </header>

        {/* Chat Container */}
        <div className="chat-container" ref={chatContainerRef}>
          {messages.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">💬</div>
              <h3>Welcome to Luna!</h3>
              <p>Start a conversation by typing a message below</p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                {message.role === 'assistant' && (
                  <div className="avatar assistant">🌙</div>
                )}
                <div className="message-content">
                  {message.content}
                  {message.files && message.files.length > 0 && (
                    <div className="message-files">
                      {message.files.map((file, i) => (
                        <span key={i} className="file-tag">📎 {file}</span>
                      ))}
                    </div>
                  )}
                </div>
                {message.role === 'user' && (
                  <div className="avatar user">👤</div>
                )}
              </div>
            ))
          )}
          
          {isTyping && (
            <div className="message assistant">
              <div className="avatar assistant">🌙</div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span>Luna is typing</span>
                  <div className="dots">
                    <div className="dot"></div>
                    <div className="dot"></div>
                    <div className="dot"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="input-wrapper">
          {uploadedFiles.length > 0 && (
            <div className="file-list">
              {uploadedFiles.map((file, index) => (
                <span key={index} className="file-badge">
                  📎 {file}
                  <button onClick={() => removeFile(index)} className="remove-file">
                    <XIcon />
                  </button>
                </span>
              ))}
            </div>
          )}
          
          <div className="input-container">
            <div className="upload-wrapper">
              <button 
                className="upload-btn" 
                onClick={() => setShowUploadMenu(!showUploadMenu)}
              >
                <PaperclipIcon />
              </button>
              
              {showUploadMenu && (
                <div className="upload-menu">
                  <button onClick={() => fileInputRef.current?.click()}>
                    <ImageIcon />
                    <span>Upload Image</span>
                  </button>
                  <button onClick={() => fileInputRef.current?.click()}>
                    <FileTextIcon />
                    <span>Upload Document</span>
                  </button>
                </div>
              )}
              
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,.pdf,.txt,.doc,.docx,.csv,.xlsx"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </div>

            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              className="message-input"
            />

            <button className="send-btn" onClick={sendMessage}>
              <SendIcon />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
