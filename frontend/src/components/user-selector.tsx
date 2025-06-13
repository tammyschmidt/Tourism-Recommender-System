"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Search, User } from "lucide-react"

interface UserSelectorProps {
  onUserChange: (user: string) => void
}

const sampleUsers = [
  {
    id: "anna_m",
    name: "Anna Miller",
    preferences: ["Italian", "Vegetarian"],
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "max_s",
    name: "Max Smith",
    preferences: ["Asian", "Spicy"],
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "lisa_k",
    name: "Lisa Klein",
    preferences: ["French", "Fine Dining"],
    avatar: "/placeholder.svg?height=40&width=40",
  },
  {
    id: "tom_w",
    name: "Tom Weber",
    preferences: ["American", "Burgers"],
    avatar: "/placeholder.svg?height=40&width=40",
  },
  { id: "sara_b", name: "Sara Bauer", preferences: ["Vegan", "Healthy"], avatar: "/placeholder.svg?height=40&width=40" },
]

export default function UserSelector({ onUserChange }: UserSelectorProps) {
  const [selectedUser, setSelectedUser] = useState("")
  const [searchTerm, setSearchTerm] = useState("")

  const filteredUsers = sampleUsers.filter((user) => user.name.toLowerCase().includes(searchTerm.toLowerCase()))

  const handleUserSelect = (userId: string, userName: string) => {
    const newUser = selectedUser === userId ? "" : userId
    setSelectedUser(newUser)
    onUserChange(newUser ? userName : "")
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <Input
          placeholder="Search for users..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pr-10"
        />
        <Search className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
      </div>

      <div className="space-y-2">
        {filteredUsers.map((user) => (
          <Button
            key={user.id}
            variant={selectedUser === user.id ? "default" : "outline"}
            className="w-full h-auto p-3 justify-start"
            onClick={() => handleUserSelect(user.id, user.name)}
          >
            <Avatar className="h-8 w-8 mr-3">
              <AvatarImage src={user.avatar || "/placeholder.svg"} alt={user.name} />
              <AvatarFallback>
                <User className="h-4 w-4" />
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 text-left">
              <div className="font-medium">{user.name}</div>
              <div className="flex gap-1 mt-1">
                {user.preferences.map((pref) => (
                  <Badge key={pref} variant="secondary" className="text-xs">
                    {pref}
                  </Badge>
                ))}
              </div>
            </div>
          </Button>
        ))}
      </div>

      {selectedUser && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 text-blue-800">
            <User className="w-4 h-4" />
            <span className="font-medium">
              Recommendation based on {sampleUsers.find((u) => u.id === selectedUser)?.name}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}