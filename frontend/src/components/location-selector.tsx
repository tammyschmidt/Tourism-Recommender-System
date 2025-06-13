import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { MapPin, Building, Search } from "lucide-react"

interface LocationSelectorProps {
  onLocationChange: (location: string) => void
}

const popularRestaurants = [
  "Zur Letzten Instanz, Berlin",
  "Ratskeller, Munich",
  "Peters Brauhaus, Cologne",
  "Hanse-Kogge, Hamburg",
  "Goldener Hirsch, Salzburg",
]

const popularCities = [
  "Berlin",
  "Munich",
  "Hamburg",
  "Cologne",
  "Frankfurt",
  "Stuttgart",
  "Düsseldorf",
  "Leipzig",
  "Dresden",
  "Hanover",
]

export default function LocationSelector({ onLocationChange }: LocationSelectorProps) {
  const [selectedLocation, setSelectedLocation] = useState("")
  const [customLocation, setCustomLocation] = useState("")

  const handleLocationSelect = (location: string) => {
    setSelectedLocation(location)
    onLocationChange(location)
  }

  const handleCustomLocationSubmit = () => {
    if (customLocation.trim()) {
      handleLocationSelect(customLocation.trim())
    }
  }

  return (
    <Tabs defaultValue="restaurant" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="restaurant" className="text-xs">
          Restaurant
        </TabsTrigger>
        <TabsTrigger value="location" className="text-xs">
          Enter Location
        </TabsTrigger>
        <TabsTrigger value="city" className="text-xs">
          Select City
        </TabsTrigger>
      </TabsList>

      <TabsContent value="restaurant" className="space-y-3">
        <Label className="text-sm font-medium">Popular restaurants</Label>
        <div className="grid gap-2">
          {popularRestaurants.map((restaurant) => (
            <Button
              key={restaurant}
              variant={selectedLocation === restaurant ? "default" : "outline"}
              className="justify-start h-auto p-3 text-left"
              onClick={() => handleLocationSelect(restaurant)}
            >
              <Building className="w-4 h-4 mr-2 flex-shrink-0" />
              <span className="truncate">{restaurant}</span>
            </Button>
          ))}
        </div>
      </TabsContent>

      <TabsContent value="location" className="space-y-3">
        <Label htmlFor="custom-location" className="text-sm font-medium">
          Enter address or location
        </Label>
        <div className="flex gap-2">
          <Input
            id="custom-location"
            placeholder="e.g., Alexanderplatz, Berlin or 10178"
            value={customLocation}
            onChange={(e) => setCustomLocation(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleCustomLocationSubmit()}
          />
          <Button onClick={handleCustomLocationSubmit} size="icon">
            <Search className="w-4 h-4" />
          </Button>
        </div>
      </TabsContent>

      <TabsContent value="city" className="space-y-3">
        <Label className="text-sm font-medium">Choose city</Label>
        <div className="flex flex-wrap gap-2">
          {popularCities.map((city) => (
            <Badge
              key={city}
              variant={selectedLocation === city ? "default" : "outline"}
              className="cursor-pointer hover:bg-primary hover:text-primary-foreground"
              onClick={() => handleLocationSelect(city)}
            >
              <MapPin className="w-3 h-3 mr-1" />
              {city}
            </Badge>
          ))}
        </div>
      </TabsContent>

      {selectedLocation && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 text-green-800">
            <MapPin className="w-4 h-4" />
            <span className="font-medium">Selected: {selectedLocation}</span>
          </div>
        </div>
      )}
    </Tabs>
  )
}