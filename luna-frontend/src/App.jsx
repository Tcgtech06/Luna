import { useState, useRef, useEffect } from 'react'
import './App.css'
import axios from 'axios'

// Configure axios base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://tcgtech-luna-chatbot.hf.space'
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Icon components
const MenuIcon = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <rect x="8" y="5" width="16" height="4" rx="2" fill="#ea4335"></rect>
    <rect x="3" y="13" width="26" height="4" rx="2" fill="#34a853"></rect>
    <rect x="8" y="21" width="16" height="4" rx="2" fill="#fbbc05"></rect>
  </svg>
)

const MessageSquareIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
  </svg>
)

const PlusIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
)

const TrashIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polyline points="3 6 5 6 21 6"></polyline>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
  </svg>
)

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

const SparklesIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4"></path>
  </svg>
)

const UserIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
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
  </svg>
)

const XIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
)

const StopIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <rect x="6" y="6" width="12" height="12" rx="2"></rect>
  </svg>
)

// Predefined questions
const PREDEFINED_QUESTIONS = [
  "Tell me about yourself",
  "What is your name?",
  "Thanglish la Pesu Luna",
  "How can you help me?",
]

function App() {
  const [theme, setTheme] = useState(() => {
    // Load theme from localStorage or default to 'light'
    return localStorage.getItem('luna-theme') || 'light'
  })
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [showUploadMenu, setShowUploadMenu] = useState(false)
  const [languageMode, setLanguageMode] = useState('english') // 'english', 'tanglish', 'tamil'
  const chatContainerRef = useRef(null)
  const fileInputRef = useRef(null)
  const abortControllerRef = useRef(null)

  const [chatHistory, setChatHistory] = useState(() => {
    try {
      const saved = localStorage.getItem('luna-history')
      return saved ? JSON.parse(saved) : []
    } catch (e) {
      console.error('Error loading history:', e)
      return []
    }
  })
  const [currentChatId, setCurrentChatId] = useState(() => {
    return localStorage.getItem('luna-current-chat-id') || null
  })
  const [isSidebarOpen, setIsSidebarOpen] = useState(() => {
    // Open by default only on mobile, closed on desktop
    return window.innerWidth <= 768
  })

  const deleteChat = (e, id) => {
    e.stopPropagation()
    setChatHistory(prev => {
      const updatedHistory = prev.filter(c => c.id !== id)
      if (currentChatId === id) {
        setCurrentChatId(null)
        setMessages([])
      }
      return updatedHistory
    })
  }

  // Load chat on mount or currentChatId change
  useEffect(() => {
    if (currentChatId) {
      const chat = chatHistory.find(c => c.id === currentChatId)
      if (chat) {
        setMessages(chat.messages || [])
      }
    } else {
      setMessages([])
    }
    localStorage.setItem('luna-current-chat-id', currentChatId || '')
  }, [currentChatId, chatHistory])

  // Save chat history to localStorage
  useEffect(() => {
    localStorage.setItem('luna-history', JSON.stringify(chatHistory))
  }, [chatHistory])

  const selectChat = (id) => {
    setCurrentChatId(id)
    // Only close sidebar on mobile (max-width: 768px)
    if (window.innerWidth <= 768) {
      setIsSidebarOpen(false)
    }
  }

  const startNewChat = () => {
    const newId = Date.now().toString()
    setCurrentChatId(newId)
    setMessages([])
    // Only close sidebar on mobile
    if (window.innerWidth <= 768) {
      setIsSidebarOpen(false)
    }
  }

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages, isTyping])

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showUploadMenu && !event.target.closest('.upload-wrapper')) {
        setShowUploadMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showUploadMenu])

  // Save theme to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('luna-theme', theme)
  }, [theme])

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  // Detect language from message
  const detectLanguage = (text) => {
    // Check for Tamil Unicode characters
    const tamilRegex = /[\u0B80-\u0BFF]/
    // Check for common Tanglish patterns (Tamil words in English script)
    const tanglishPatterns = /\b(da|di|pa|po|la|le|na|ne|enna|epdi|yenna|sollu|podu|vaa|po|iru|vandhu|pona|pannitu|pannu|thaan|dhan|illa|illaiya|aama|seri|ok|super|nalla|romba|konjam|oru|rendu|moonu|naalu)\b/i
    
    if (tamilRegex.test(text)) {
      return 'tamil'
    } else if (tanglishPatterns.test(text)) {
      return 'tanglish'
    }
    return 'english'
  }

  // Get language instruction for API
  const getLanguageInstruction = () => {
    if (languageMode === 'tanglish') {
      return ' [IMPORTANT: Reply ONLY in Tanglish (Tamil words written in English script). Do not use pure Tamil or pure English. Mix Tamil and English naturally like: "Naan oru AI assistant da. Unakku epdi help panna mudiyum?"]'
    } else if (languageMode === 'tamil') {
      return ' [IMPORTANT: Reply ONLY in Tamil language using Tamil script.]'
    }
    return ''
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

  const sendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim()) return

    // Detect language from user message and update mode
    const detectedLang = detectLanguage(messageText)
    if (detectedLang !== 'english') {
      setLanguageMode(detectedLang)
    } else if (messageText.toLowerCase().includes('english') || 
               messageText.toLowerCase().includes('speak english')) {
      setLanguageMode('english')
    }

    const userMessage = {
      role: 'user',
      content: messageText,
      files: uploadedFiles
    }

    const updatedMessages = [...messages, userMessage]
    setMessages(updatedMessages)
    setInputMessage('')
    setIsTyping(true)

    // Get or create chat ID
    const chatId = currentChatId || Date.now().toString()
    
    // Update current chat ID if it's a new chat
    if (!currentChatId) {
      setCurrentChatId(chatId)
    }

    // Update history with user message
    const existingChat = chatHistory.find(chat => chat.id === chatId)
    let updatedHistory
    
    if (!existingChat) {
      // Create new chat entry
      updatedHistory = [...chatHistory, {
        id: chatId,
        title: messageText.substring(0, 30) + (messageText.length > 30 ? '...' : ''),
        messages: updatedMessages,
        timestamp: new Date().toISOString()
      }]
    } else {
      // Update existing chat entry
      updatedHistory = chatHistory.map(chat => 
        chat.id === chatId 
          ? { ...chat, messages: updatedMessages, timestamp: new Date().toISOString() }
          : chat
      )
    }
    setChatHistory(updatedHistory)

    // Create new AbortController for this request
    abortControllerRef.current = new AbortController()
    const messageWithInstruction = messageText + getLanguageInstruction()

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: messageWithInstruction,
        files: uploadedFiles
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        signal: abortControllerRef.current.signal
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response
      }

      const finalMessages = [...updatedMessages, assistantMessage]
      setMessages(finalMessages)
      
      // Update history with assistant response
      const finalHistory = updatedHistory.map(chat => 
        chat.id === chatId 
          ? { ...chat, messages: finalMessages, timestamp: new Date().toISOString() }
          : chat
      )
      setChatHistory(finalHistory)
      
      setUploadedFiles([])
    } catch (error) {
      if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        const cancelMessage = {
          role: 'assistant',
          content: 'Response stopped by user.'
        }
        const finalMessages = [...updatedMessages, cancelMessage]
        setMessages(finalMessages)
        setChatHistory(updatedHistory.map(chat => 
          chat.id === chatId ? { ...chat, messages: finalMessages } : chat
        ))
      } else {
        console.error('Error sending message:', error)
        const errorMessage = {
          role: 'assistant',
          content: `Sorry, an error occurred: ${error.response?.data?.error || error.message || 'Please try again.'}`
        }
        const finalMessages = [...updatedMessages, errorMessage]
        setMessages(finalMessages)
        setChatHistory(updatedHistory.map(chat => 
          chat.id === chatId ? { ...chat, messages: finalMessages } : chat
        ))
      }
    } finally {
      setIsTyping(false)
      abortControllerRef.current = null
    }
  }

  const stopResponse = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsTyping(false)
    }
  }

  const handlePredefinedQuestion = (question) => {
    // Set language mode based on predefined question
    if (question === "Thanglish la Pesu Luna") {
      setLanguageMode('tanglish')
    }
    sendMessage(question)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className={`app ${theme}`}>
      {/* Background Pattern */}
      <div className="celestial-background">
        <div className="star star-1"></div>
        <div className="star star-2"></div>
        <div className="star star-3"></div>
        <div className="star star-4"></div>
        <div className="star star-5"></div>
        <div className="moon-pattern"></div>
        <div className="comet comet-1"></div>
        <div className="comet comet-2"></div>
      </div>

      {/* Sidebar Overlay */}
      {isSidebarOpen && (
        <div className="sidebar-overlay" onClick={() => setIsSidebarOpen(false)}></div>
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={startNewChat}>
            <PlusIcon />
            <span>New Chat</span>
          </button>
        </div>
        <div className="sidebar-content">
          <div className="history-label">Recent</div>
          <div className="history-list">
            {chatHistory.length === 0 ? (
              <div className="empty-history">No history yet</div>
            ) : (
              chatHistory.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)).map(chat => (
                <div 
                  key={chat.id} 
                  className={`history-item ${currentChatId === chat.id ? 'active' : ''}`}
                  onClick={() => selectChat(chat.id)}
                >
                  <MessageSquareIcon />
                  <span className="history-title">{chat.title}</span>
                  <button className="delete-chat" onClick={(e) => deleteChat(e, chat.id)}>
                    <TrashIcon />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </aside>

      <div className="main-content">
        {/* Header */}
        <header className="header">
          <div className="header-left">
            <button className="menu-btn" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
              <MenuIcon />
            </button>
            <div className="logo">
              <img src="/logo.gif" alt="Luna Logo" />
            </div>
            <div className="header-title">
              <h1>Luna</h1>
            </div>
          </div>
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
          </button>
        </header>


      {/* Chat Container */}
      <div className="chat-container" ref={chatContainerRef}>
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <SparklesIcon />
            </div>
            <h2>Hello, I'm Luna</h2>
            <p>How can I help you today?</p>
            
            {/* Predefined Questions */}
            <div className="predefined-questions">
              {PREDEFINED_QUESTIONS.map((question, index) => (
                <button
                  key={index}
                  className="question-card"
                  onClick={() => handlePredefinedQuestion(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-avatar">
                {message.role === 'assistant' ? <img src="/logo.gif" alt="Luna" /> : <UserIcon />}
              </div>
              <div className="message-content">
                {message.content}
                {message.files && message.files.length > 0 && (
                  <div className="message-files">
                    {message.files.map((file, i) => (
                      <span key={i} className="file-tag">
                        <FileTextIcon /> {file}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {isTyping && (
          <div className="message assistant">
            <div className="message-avatar">
              <img src="/logo.gif" alt="Luna" />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="input-wrapper">
        <div className="input-container-wrapper">
          {uploadedFiles.length > 0 && (
            <div className="file-list">
              {uploadedFiles.map((file, index) => (
                <span key={index} className="file-badge">
                  <FileTextIcon /> {file}
                  <button onClick={() => removeFile(index)} className="remove-file" aria-label="Remove file">
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
                aria-label="Attach file"
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
              placeholder="Ask Luna anything..."
              className="message-input"
            />

            <button 
              className="send-btn" 
              onClick={isTyping ? stopResponse : () => sendMessage()}
              disabled={!isTyping && !inputMessage.trim()}
              aria-label={isTyping ? "Stop response" : "Send message"}
            >
              {isTyping ? <StopIcon /> : <SendIcon />}
            </button>
          </div>
        </div>
      </div>
      </div>
    </div>
  )
}

export default App
