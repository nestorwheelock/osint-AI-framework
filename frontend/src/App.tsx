import { Routes, Route } from 'react-router-dom'
import { Container, AppBar, Toolbar, Typography, Box } from '@mui/material'
import { Search as SearchIcon } from '@mui/icons-material'

import SubjectManager from './components/SubjectManager'
import { APIProvider } from './contexts/APIContext'

function App() {
  return (
    <APIProvider>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <SearchIcon sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              OSINT Framework
            </Typography>
          </Toolbar>
        </AppBar>
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Routes>
            <Route path="/" element={<SubjectManager />} />
            <Route path="/subjects" element={<SubjectManager />} />
          </Routes>
        </Container>
      </Box>
    </APIProvider>
  )
}

export default App
