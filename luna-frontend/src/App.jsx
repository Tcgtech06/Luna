import { useState, useRef, useEffect } from 'react'
import { Moon, Sun, Paperclip, Send, Image, FileText, X } from 'lucide-react'
import './App.css'
import axios from 'axios'

// Configure axios base URL - change this to your Hugging Face Space URL when deployed
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:7860'

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

  const handleFileUpload = (event, type) => {
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
            {theme === 'dark' ? <Moon size={20} /> : <Sun size={20} />}
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
                    <X size={14} />
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
                <Paperclip size={20} />
              </button>
              
              {showUploadMenu && (
                <div className="upload-menu">
                  <button onClick={() => fileInputRef.current?.click()}>
                    <Image size={18} />
                    <span>Upload Image</span>
                  </button>
                  <button onClick={() => fileInputRef.current?.click()}>
                    <FileText size={18} />
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
              <Send size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
