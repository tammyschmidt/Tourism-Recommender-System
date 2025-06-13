import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Heart, Users, Briefcase, Coffee, Music, Utensils } from "lucide-react"

interface SettingSelectorProps {
  onSettingChange: (setting: string) => void
}

const settings = [
  { id: "romantic", label: "Romantic", icon: Heart, description: "Perfect for a date" },
  { id: "family", label: "Family-Friendly", icon: Users, description: "Good for families with children" },
  { id: "business", label: "Business", icon: Briefcase, description: "Ideal for business meals" },
  { id: "casual", label: "Casual", icon: Coffee, description: "Relaxed atmosphere" },
  { id: "lively", label: "Lively", icon: Music, description: "Vibrant, energetic mood" },
  { id: "fine-dining", label: "Fine Dining", icon: Utensils, description: "Upscale cuisine and service" },
]

export default function SettingSelector({ onSettingChange }: SettingSelectorProps) {
  const [selectedSetting, setSelectedSetting] = useState("")

  const handleSettingSelect = (settingId: string) => {
    const newSetting = selectedSetting === settingId ? "" : settingId
    setSelectedSetting(newSetting)
    onSettingChange(newSetting)
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {settings.map((setting) => {
          const Icon = setting.icon
          const isSelected = selectedSetting === setting.id

          return (
            <Button
              key={setting.id}
              variant={isSelected ? "default" : "outline"}
              className="h-auto p-4 flex flex-col items-start text-left"
              onClick={() => handleSettingSelect(setting.id)}
            >
              <div className="flex items-center gap-2 mb-1">
                <Icon className="w-4 h-4" />
                <span className="font-medium">{setting.label}</span>
              </div>
              <span className="text-xs opacity-80">{setting.description}</span>
            </Button>
          )
        })}
      </div>
    </div>
  )
}