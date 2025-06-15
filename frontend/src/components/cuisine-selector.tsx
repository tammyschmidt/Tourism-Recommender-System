import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { X, Search } from "lucide-react"

interface CuisineSelectorProps {
  onCuisinesChange: (cuisines: string[]) => void
}

const popularCuisines = [
  "German",
  "Italian",
  "Asian",
  "French",
  "Greek",
  "Turkish",
  "Indian",
  "Mexican",
  "Japanese",
  "Thai",
  "Chinese",
  "American",
  "Spanish",
  "Vegetarian",
  "Vegan",
]

export default function CuisineSelector({ onCuisinesChange }: CuisineSelectorProps) {
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>([])
  const [searchTerm, setSearchTerm] = useState("")

  const filteredCuisines = popularCuisines.filter(
    (cuisine) => cuisine.toLowerCase().includes(searchTerm.toLowerCase()) && !selectedCuisines.includes(cuisine),
  )

  const handleCuisineAdd = (cuisine: string) => {
    const newCuisines = [...selectedCuisines, cuisine]
    setSelectedCuisines(newCuisines)
    onCuisinesChange(newCuisines)
    setSearchTerm("")
  }

  const handleCuisineRemove = (cuisine: string) => {
    const newCuisines = selectedCuisines.filter((c) => c !== cuisine)
    setSelectedCuisines(newCuisines)
    onCuisinesChange(newCuisines)
  }

  const handleCustomCuisine = () => {
    if (searchTerm.trim() && !selectedCuisines.includes(searchTerm.trim())) {
      handleCuisineAdd(searchTerm.trim())
    }
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <Input
          placeholder="Search or enter a cuisine..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && handleCustomCuisine()}
          className="pr-10"
        />
        <Button size="icon" variant="ghost" className="absolute right-1 top-1 h-8 w-8" onClick={handleCustomCuisine}>
          <Search className="w-4 h-4" />
        </Button>
      </div>

      {selectedCuisines.length > 0 && (
        <div>
          <Label className="text-sm font-medium mb-2 block">Chosen cuisines:</Label>
          <div className="flex flex-wrap gap-2">
            {selectedCuisines.map((cuisine) => (
              <Badge key={cuisine} variant="default" className="flex items-center gap-1">
                {cuisine}
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-4 w-4 p-0 hover:bg-transparent"
                  onClick={() => handleCuisineRemove(cuisine)}
                >
                  <X className="w-3 h-3" />
                </Button>
              </Badge>
            ))}
          </div>
        </div>
      )}

      {filteredCuisines.length > 0 && (
        <div>
          <Label className="text-sm font-medium mb-2 block">
            {searchTerm ? "Search results:" : "Popular cuisines:"}
          </Label>
          <div className="flex flex-wrap gap-2">
            {filteredCuisines.slice(0, 10).map((cuisine) => (
              <Badge
                key={cuisine}
                variant="outline"
                className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
                onClick={() => handleCuisineAdd(cuisine)}
              >
                {cuisine}
              </Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}