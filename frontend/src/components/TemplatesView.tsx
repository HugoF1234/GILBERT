import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Container,
  keyframes,
  styled,
  alpha,
  Button,
  Stack,
  Chip,
  Avatar,
  AvatarGroup,
  ToggleButton,
  ToggleButtonGroup,
  Divider,
} from '@mui/material';
import { 
  Description as DescriptionIcon, 
  Lock as LockIcon,
  AutoAwesome as AutoAwesomeIcon,
  Business as BusinessIcon,
  Code as CodeIcon,
  Assignment as AssignmentIcon,
  School as SchoolIcon,
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

// Animations sophistiquées
const floatAnimation = keyframes`
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  25% {
    transform: translateY(-20px) rotate(1deg);
  }
  50% {
    transform: translateY(-10px) rotate(-1deg);
  }
  75% {
    transform: translateY(-15px) rotate(0.5deg);
  }
`;

const slideInAnimation = keyframes`
  0% {
    transform: translateX(100vw) scale(0.9);
    opacity: 0;
  }
  10% {
    opacity: 0.25;
  }
  90% {
    opacity: 0.25;
  }
  100% {
    transform: translateX(-100vw) scale(0.9);
    opacity: 0;
  }
`;

const pulseAnimation = keyframes`
  0%, 100% {
    opacity: 0.3;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.05);
  }
`;

// Composant de template flottant sophistiqué
const FloatingTemplate = styled(Paper)(({ theme }) => ({
  position: 'absolute',
  padding: theme.spacing(2.5),
  minWidth: 280,
  height: 120,
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'space-between',
  background: `linear-gradient(135deg, 
    ${alpha(theme.palette.primary.main, 0.06)} 0%, 
    ${alpha(theme.palette.secondary.main, 0.04)} 50%,
    ${alpha(theme.palette.info.main, 0.06)} 100%)`,
  border: `1px solid ${alpha(theme.palette.primary.main, 0.12)}`,
  borderRadius: theme.spacing(2.5),
  animation: `${slideInAnimation} 24s linear infinite`,
  backdropFilter: 'blur(6px)',
  boxShadow: `0 4px 16px ${alpha(theme.palette.primary.main, 0.06)}`,
  transform: 'translateX(100vw)', // Commence hors écran à droite
  filter: 'blur(0.5px)', // Flou très léger
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: `linear-gradient(45deg, 
      ${alpha('#3B82F6', 0.015)} 0%, 
      ${alpha('#8B5CF6', 0.015)} 50%, 
      ${alpha('#06B6D4', 0.015)} 100%)`,
    borderRadius: 'inherit',
    zIndex: -1,
  }
}));

// Éléments décoratifs flottants
const FloatingDecoration = styled(Box)(({ theme }) => ({
  position: 'absolute',
  width: 60,
  height: 60,
  borderRadius: '50%',
  background: `linear-gradient(135deg, 
    ${alpha(theme.palette.primary.main, 0.1)} 0%, 
    ${alpha(theme.palette.secondary.main, 0.1)} 100%)`,
  animation: `${floatAnimation} 6s ease-in-out infinite`,
  backdropFilter: 'blur(5px)',
}));

const PulsingOrb = styled(Box)(({ theme }) => ({
  position: 'absolute',
  width: 120,
  height: 120,
  borderRadius: '50%',
  background: `radial-gradient(circle, 
    ${alpha(theme.palette.primary.main, 0.1)} 0%, 
    ${alpha(theme.palette.primary.main, 0.05)} 50%, 
    transparent 70%)`,
  animation: `${pulseAnimation} 4s ease-in-out infinite`,
}));

const templates = [
  { 
    id: 1, 
    title: 'Réunion Hebdomadaire', 
    description: 'Suivi d\'équipe et points d\'avancement',
    icon: <AssignmentIcon sx={{ fontSize: 28, color: '#3B82F6' }} />,
    category: 'Équipe',
    avatars: [
      'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1494790108755-2616b332c647?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 2, 
    title: 'Négociation Commerciale', 
    description: 'Suivi des deals et décisions business',
    icon: <BusinessIcon sx={{ fontSize: 28, color: '#10B981' }} />,
    category: 'Business',
    avatars: [
      'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 3, 
    title: 'Revue Technique', 
    description: 'Spécifications et architecture',
    icon: <CodeIcon sx={{ fontSize: 28, color: '#8B5CF6' }} />,
    category: 'Tech',
    avatars: [
      'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 4, 
    title: 'Planification Projet', 
    description: 'Jalons et roadmap produit',
    icon: <TimelineIcon sx={{ fontSize: 28, color: '#F59E0B' }} />,
    category: 'Projet',
    avatars: [
      'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 5, 
    title: 'Stratégie Entreprise', 
    description: 'Orientations et décisions clés',
    icon: <AutoAwesomeIcon sx={{ fontSize: 28, color: '#EF4444' }} />,
    category: 'Stratégie',
    avatars: [
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 6, 
    title: 'Session Formation', 
    description: 'Synthèse et apprentissages',
    icon: <SchoolIcon sx={{ fontSize: 28, color: '#06B6D4' }} />,
    category: 'Formation',
    avatars: [
      'https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1552058544-f2b08422138a?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 7, 
    title: 'Comité de Direction', 
    description: 'Décisions stratégiques et gouvernance',
    icon: <BusinessIcon sx={{ fontSize: 28, color: '#7C3AED' }} />,
    category: 'Direction',
    avatars: [
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1494790108755-2616b332c647?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 8, 
    title: 'Revue Produit', 
    description: 'Roadmap et retours utilisateurs',
    icon: <TimelineIcon sx={{ fontSize: 28, color: '#EC4899' }} />,
    category: 'Produit',
    avatars: [
      'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1519345182560-3f2917c472ef?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 9, 
    title: 'Stand-up Agile', 
    description: 'Points quotidiens et blocages',
    icon: <AssignmentIcon sx={{ fontSize: 28, color: '#059669' }} />,
    category: 'Agile',
    avatars: [
      'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 10, 
    title: 'Réunion Client', 
    description: 'Présentation et feedback client',
    icon: <BusinessIcon sx={{ fontSize: 28, color: '#DC2626' }} />,
    category: 'Client',
    avatars: [
      'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1463453091185-61582044d556?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 11, 
    title: 'Revue de Code', 
    description: 'Qualité et bonnes pratiques',
    icon: <CodeIcon sx={{ fontSize: 28, color: '#7C2D12' }} />,
    category: 'Dev',
    avatars: [
      'https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1552058544-f2b08422138a?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&h=150&fit=crop&crop=face'
    ]
  },
  { 
    id: 12, 
    title: 'Bilan Trimestriel', 
    description: 'Résultats et objectifs',
    icon: <AutoAwesomeIcon sx={{ fontSize: 28, color: '#1E40AF' }} />,
    category: 'Finance',
    avatars: [
      'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150&h=150&fit=crop&crop=face',
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face'
    ]
  },
];

const TemplatesView: React.FC = () => {
  return (
    <Box
      sx={{
        position: 'relative',
        height: '100vh',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `radial-gradient(circle at 20% 80%, 
            ${alpha('#3B82F6', 0.03)} 0%, 
            transparent 50%),
          radial-gradient(circle at 80% 20%, 
            ${alpha('#8B5CF6', 0.03)} 0%, 
            transparent 50%),
          radial-gradient(circle at 40% 40%, 
            ${alpha('#06B6D4', 0.02)} 0%, 
            transparent 50%)`,
          zIndex: 0,
        }
      }}
    >
      {/* Éléments décoratifs d'arrière-plan */}
      <PulsingOrb sx={{ top: '10%', left: '15%', animationDelay: '0s' }} />
      <PulsingOrb sx={{ top: '60%', right: '20%', animationDelay: '2s' }} />
      <PulsingOrb sx={{ bottom: '20%', left: '10%', animationDelay: '1s' }} />
      
      <FloatingDecoration sx={{ top: '20%', right: '10%', animationDelay: '0s' }} />
      <FloatingDecoration sx={{ top: '70%', left: '5%', animationDelay: '2s' }} />
      <FloatingDecoration sx={{ top: '40%', right: '25%', animationDelay: '4s' }} />

      {/* Templates qui défilent en arrière-plan */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          overflow: 'hidden',
          zIndex: 0,
        }}
      >
        {templates.map((template, index) => (
          <FloatingTemplate
            key={template.id}
            sx={{
              top: `${8 + (index * 8)}%`, // Espacement réduit pour plus de templates
              // Délais négatifs et positifs pour avoir des templates déjà présents
              animationDelay: `${-20 + (index * 3)}s`, // Ajusté pour la nouvelle durée
              animationDuration: `${22 + index * 1.5}s`, // Durées plus lentes
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  background: alpha('#fff', 0.8),
                  boxShadow: `0 4px 12px ${alpha('#000', 0.05)}`,
                }}
              >
                {template.icon}
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontWeight: 700, 
                    mb: 0.5,
                    color: '#1E293B',
                    fontSize: '1.1rem'
                  }}
                >
                  {template.title}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: '#64748B',
                    fontSize: '0.9rem',
                    lineHeight: 1.4
                  }}
                >
                  {template.description}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
              <Chip 
                label={template.category}
                size="small"
                sx={{
                  backgroundColor: alpha('#3B82F6', 0.1),
                  color: '#3B82F6',
                  fontWeight: 600,
                  fontSize: '0.75rem'
                }}
              />
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AvatarGroup 
                  max={3}
                  sx={{
                    '& .MuiAvatar-root': {
                      width: 24,
                      height: 24,
                      fontSize: '0.75rem',
                      border: '2px solid white',
                      boxShadow: `0 2px 4px ${alpha('#000', 0.1)}`,
                    }
                  }}
                >
                  {template.avatars.map((avatar, avatarIndex) => (
                    <Avatar 
                      key={avatarIndex}
                      src={avatar}
                      alt={`User ${avatarIndex + 1}`}
                      sx={{
                        width: 24,
                        height: 24,
                      }}
                    />
                  ))}
                </AvatarGroup>
                <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem' }}>
                  Premium
                </Typography>
              </Box>
            </Box>
          </FloatingTemplate>
        ))}
      </Box>

      {/* Interface principale (remplacée: affichage Premium) */}
      <Container
        maxWidth="md"
        sx={{
          position: 'relative',
          zIndex: 2,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100%',
          textAlign: 'center',
        }}
      >
        <Paper
          elevation={0}
          sx={{
            p: { xs: 3, md: 4 },
            borderRadius: 2,
            background: `linear-gradient(135deg, 
              ${alpha('#fff', 0.98)} 0%, 
              ${alpha('#fff', 0.95)} 100%)`,
            backdropFilter: 'blur(20px)',
            border: `1px solid ${alpha('#E2E8F0', 0.6)}`,
            boxShadow: `0 8px 32px ${alpha('#000', 0.04)}`,
            maxWidth: 560,
            width: '100%',
            position: 'relative',
          }}
        >
          <Stack spacing={2} alignItems="center">
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#1E293B' }}>
              Choisissez un type de template intégré
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748B', mb: 1, textAlign: 'center' }}>
              Ces templates embarqués sont disponibles immédiatement.
            </Typography>
            <ToggleButtonGroup exclusive aria-label="template-type" sx={{ mb: 2 }}>
              <ToggleButton value="default" onClick={() => { try { localStorage.setItem('default_template_type', 'default'); } catch {} }}>
                Par défaut
              </ToggleButton>
              <ToggleButton value="formation" onClick={() => { try { localStorage.setItem('default_template_type', 'formation'); } catch {} }}>
                Formation
              </ToggleButton>
            </ToggleButtonGroup>
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} sx={{ width: '100%' }}>
              <Paper variant="outlined" sx={{ flex: 1, p: 2, borderRadius: 2 }}>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <AssignmentIcon sx={{ color: '#3B82F6' }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Par défaut</Typography>
                  <CheckCircleIcon sx={{ color: '#22C55E', ml: 'auto' }} />
                </Stack>
                <Typography variant="body2" sx={{ color: '#64748B', mt: 1 }}>
                  Format standard pour tout type de réunion.
                </Typography>
              </Paper>
              <Paper variant="outlined" sx={{ flex: 1, p: 2, borderRadius: 2 }}>
                <Stack direction="row" alignItems="center" spacing={1}>
                  <SchoolIcon sx={{ color: '#06B6D4' }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>Formation</Typography>
                </Stack>
                <Typography variant="body2" sx={{ color: '#64748B', mt: 1 }}>
                  Compte rendu orienté apprentissages et exercices.
                </Typography>
              </Paper>
            </Stack>
            <Divider sx={{ my: 1, width: '100%' }} />
            <Typography variant="body2" sx={{ color: '#94A3B8' }}>
              Les templates personnalisés restent Premium.
            </Typography>
          </Stack>
        </Paper>
      </Container>
    </Box>
  );
};

export default TemplatesView; 
