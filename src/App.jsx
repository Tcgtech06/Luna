import { useState, useRef, useEffect } from 'react'
import './App.css'
import axios from 'axios'

// Configure axios base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://tcgtech-luna-chatbot.hf.space'
axios.defaults.headers.common['Content-Type'] = 'application/json'

console.log('API_BASE_URL:', API_BASE_URL) // Debug log

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

const HeartIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78 7.78 7.78 0 0 0 7.78 0l-1.06 1.06L12 17.23l-1.06-1.06a5.5 5.5 0 0 0-7.78-7.78l-1.06 1.06a5.5 5.5 0 0 0 7.78 7.78l1.06 1.06L12 21.23z"/>
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

const LoveIcon = () => (
  <img 
    src="/love.png" 
    alt="Love" 
    width="20" 
    height="20" 
    style={{ 
      objectFit: 'contain',
      filter: 'drop-shadow(0 0 4px rgba(233, 30, 99, 0.3))'
    }} 
  />
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
  const [isUploading, setIsUploading] = useState(false)
  const [uploadedDocuments, setUploadedDocuments] = useState([]) // Track processed documents
  const [isRelationshipMode, setIsRelationshipMode] = useState(false) // Relationship consultant mode
  const [languageMode, setLanguageMode] = useState('english') // 'english', 'tanglish', 'tamil'
  const [userProfile, setUserProfile] = useState(() => {
    try {
      const saved = localStorage.getItem('luna-user-profile')
      return saved ? JSON.parse(saved) : { user_id: 'user_' + Date.now(), preferences: {} }
    } catch (e) {
      console.error('Error loading user profile:', e)
      return { user_id: 'user_' + Date.now(), preferences: {} }
    }
  })
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
    // Closed by default on all devices
    return false
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

  // Save user profile to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('luna-user-profile', JSON.stringify(userProfile))
  }, [userProfile])

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

  const handleFileUpload = async (event) => {
      const files = Array.from(event.target.files)

      // Auto-close upload menu immediately when files are selected
      setShowUploadMenu(false)

      // Return early if no files selected
      if (files.length === 0) return

      // Add files to preview area (not to chat yet)
      const fileNames = files.map(f => f.name)
      setUploadedFiles([...uploadedFiles, ...fileNames])

      // Analyze all files immediately
      for (const file of files) {
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
        const isDocument = ['.pdf', '.txt'].includes(fileExtension)
        const isImage = file.type.startsWith('image/')

        // For all files, send to analyze endpoint
        if (isImage || isDocument) {
          try {
            console.log(`🔍 Analyzing ${file.name}...`)

            const formData = new FormData()
            formData.append('file', file)

            const response = await axios.post(`${API_BASE_URL}/analyze-file`, formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              },
              timeout: 120000
            })

            console.log(`✅ Analysis complete for ${file.name}`)

            // For documents, also upload to RAG system
            if (isDocument) {
              setIsUploading(true)
              try {
                const ragResponse = await axios.post(`${API_BASE_URL}/upload`, formData, {
                  headers: {
                    'Content-Type': 'multipart/form-data'
                  },
                  timeout: 120000
                })

                if (ragResponse.data.success) {
                  const newDoc = {
                    name: ragResponse.data.filename,
                    uploadTime: new Date().toISOString(),
                    chunks: ragResponse.data.chunks_created,
                    processingTime: ragResponse.data.processing_time
                  }
                  setUploadedDocuments(prev => [...prev, newDoc])
                  console.log(`✅ ${ragResponse.data.filename} ready for RAG analysis`)
                }
              } catch (error) {
                console.error('RAG upload error:', error)
              } finally {
                setIsUploading(false)
              }
            }

          } catch (error) {
            console.error(`Analysis error for ${file.name}:`, error)
          }
        }
      }

      // Clear the file input
      if (event.target) {
        event.target.value = ''
      }
    }

  const removeFile = (index) => {
    setUploadedFiles(uploadedFiles.filter((_, i) => i !== index))
  }

  // Function to make URLs clickable
  const makeUrlsClickable = (text) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g
    return text.replace(urlRegex, '<a href="$1" target="_blank" rel="noopener noreferrer" class="clickable-url">$1</a>')
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
    
    // Clear uploaded files after sending message
    setUploadedFiles([])
    
    setIsTyping(true)

    // Auto-scroll to bottom after adding user message
    setTimeout(() => {
      if (chatContainerRef.current) {
        chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
      }
    }, 100)

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
      // Update existing chat
      updatedHistory = chatHistory.map(chat => 
        chat.id === chatId 
          ? { ...chat, messages: updatedMessages, timestamp: new Date().toISOString() }
          : chat
      )
    }
    
    setChatHistory(updatedHistory)
    setCurrentChatId(chatId)
    
    abortControllerRef.current = new AbortController()
    let messageWithInstruction = messageText + getLanguageInstruction()
    
    // Remove old relationship mode instruction - let backend handle it

    try {
      console.log('Sending request to:', `${API_BASE_URL}/chat`) // Debug log
      console.log('Request payload:', {
        message: messageWithInstruction,
        files: uploadedFiles,
        conversation_history: updatedMessages.slice(-10),
        user_profile: userProfile
      }) // Debug log

      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: messageWithInstruction,
        files: uploadedFiles,
        conversation_history: updatedMessages.slice(-10), // Send last 10 messages for context
        user_profile: {
          ...userProfile,
          relationship_mode: isRelationshipMode
        }
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        signal: abortControllerRef.current.signal,
        timeout: 140000 // 140 second timeout (increased for multiple model switching)
      })

      console.log('Response received:', response.data) // Debug log

      // Process response content to make URLs clickable
      const processedContent = makeUrlsClickable(response.data.response)

      const assistantMessage = {
        role: 'assistant',
        content: processedContent
      }

      const finalMessages = [...updatedMessages, assistantMessage]
      setMessages(finalMessages)
      
      // Auto-scroll to bottom after adding assistant message
      setTimeout(() => {
        if (chatContainerRef.current) {
          chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
        }
      }, 100)
      
      // Update user profile if returned
      if (response.data.user_profile) {
        setUserProfile(response.data.user_profile)
      }
      
      // Update history with assistant response
      const finalHistory = updatedHistory.map(chat => 
        chat.id === chatId 
          ? { ...chat, messages: finalMessages, timestamp: new Date().toISOString() }
          : chat
      )
      setChatHistory(finalHistory)
      
      setUploadedFiles([])
    } catch (error) {
      console.error('Error sending message:', error)
      console.error('Error response:', error.response?.data)
      console.error('Error status:', error.response?.status)
      
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
        let errorMessage = 'Sorry, an error occurred.'
        
        if (error.code === 'ECONNABORTED') {
          errorMessage = 'Luna is switching models, please wait a moment and try again.'
        } else if (error.code === 'ECONNREFUSED') {
          errorMessage = 'Cannot connect to Luna backend.'
        } else if (error.response?.status === 404) {
          errorMessage = 'Backend service not found.'
        } else if (error.response?.status >= 500) {
          errorMessage = 'Backend server error.'
        } else if (error.response?.data?.error) {
          errorMessage = `Error: ${error.response.data.error}`
        }
        
        const errorMsg = {
          role: 'assistant',
          content: errorMessage
        }
        const finalMessages = [...updatedMessages, errorMsg]
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
    <div className={`app ${theme} ${isRelationshipMode ? 'love-mode' : ''}`}>
      {/* Background Pattern */}
      <div className="celestial-background">
        <div className="star star-1"></div>
        <div className="star star-2"></div>
        <div className="star star-3"></div>
        <div className="moon-pattern"></div>
        <div className="comet"></div>
      </div>
      
      {/* Heart Patterns for Love Mode */}
      {isRelationshipMode && (
        <div className="heart-pattern">
          <div className="heart">❤️</div>
          <div className="heart">💕</div>
          <div className="heart">💖</div>
          <div className="heart">💗</div>
          <div className="heart">💝</div>
        </div>
      )}

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
              <h1>{isRelationshipMode ? 'Cupin' : 'Luna'}</h1>
            </div>
          </div>
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
          </button>
        </header>


      {/* Chat Container */}
      <div className="chat-container" ref={chatContainerRef}>
        {/* Chat Background Hearts for Love Mode */}
        {isRelationshipMode && (
          <div className="chat-hearts">
            <div className="chat-heart">💕</div>
            <div className="chat-heart">💖</div>
            <div className="chat-heart">💗</div>
            <div className="chat-heart">💝</div>
            <div className="chat-heart">❤️</div>
            <div className="chat-heart">💕</div>
            <div className="chat-heart">💖</div>
            <div className="chat-heart">💗</div>
          </div>
        )}
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">
              <SparklesIcon />
            </div>
            <h2>Hello, I'm {isRelationshipMode ? 'Cupin' : 'Luna'}</h2>
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
                <div dangerouslySetInnerHTML={{ __html: message.content }} />
                
                {/* File information display */}
                {message.fileInfo && (
                  <div className="file-info-card">
                    <div className="file-info-header">
                      <FileTextIcon />
                      <span className="file-name">{message.fileInfo.name}</span>
                      {message.isUploading && (
                        <div className="upload-spinner">
                          <div className="spinner"></div>
                        </div>
                      )}
                    </div>
                    <div className="file-info-details">
                      <span className="file-size">{message.fileInfo.size}</span>
                      <span className="file-type">{message.fileInfo.type}</span>
                    </div>
                    {message.isUploading && (
                      <div className="upload-progress">
                        <div className="progress-bar">
                          <div className="progress-fill"></div>
                        </div>
                        <span className="upload-text">Uploading...</span>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Legacy file display for backward compatibility */}
                {message.files && message.files.length > 0 && !message.fileInfo && (
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
                  <button onClick={() => {
                    // Set file input to accept only images
                    fileInputRef.current.accept = 'image/*';
                    fileInputRef.current?.click();
                  }}>
                    <ImageIcon />
                    <span>Upload Image</span>
                  </button>
                  <button onClick={() => {
                    // Set file input to accept documents for RAG processing including ZIP
                    fileInputRef.current.accept = '.pdf,.txt,.zip,application/pdf,text/plain,application/zip,application/x-zip-compressed';
                    fileInputRef.current?.click();
                  }}>
                    <FileTextIcon />
                    <span>Upload Document (PDF/TXT/ZIP)</span>
                  </button>
                  <div className="upload-info">
                    <small>Images for chat • Documents for analysis</small>
                  </div>
                </div>
              )}
              
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </div>

            <button 
              className={`love-btn ${isRelationshipMode ? 'active' : ''}`}
              onClick={() => {
                setIsRelationshipMode(!isRelationshipMode)
                const modeMessage = {
                  role: 'assistant',
                  content: isRelationshipMode 
                    ? "General mode activated." 
                    : "💕 Relationship mode activated."
                }
                setMessages(prev => [...prev, modeMessage])
                
                // Auto-scroll
                setTimeout(() => {
                  if (chatContainerRef.current) {
                    chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
                  }
                }, 100)
              }}
              aria-label={isRelationshipMode ? "Exit relationship mode" : "Enter relationship mode"}
            >
              <LoveIcon />
            </button>

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
              disabled={(!isTyping && !inputMessage.trim()) || isUploading}
              aria-label={isTyping ? "Stop response" : isUploading ? "Uploading..." : "Send message"}
            >
              {isTyping ? <StopIcon /> : isUploading ? '⏳' : <SendIcon />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Watermark */}
      <div className="mobile-watermark">
        <span>A product of </span>
        <a 
          href="https://tcgtech.in" 
          target="_blank" 
          rel="noopener noreferrer"
          className="tcg-tech-link"
        >
          <span className="t-letter">T</span>
          <span className="c-letter">C</span>
          <span className="g-letter">G</span>
          <span className="space"> </span>
          <span className="tech-text">TECH</span>
        </a>
      </div>
      </div>
    </div>
  )
}

export default App
