import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { MapPin, Building, Search, Loader2, AlertTriangle, ExternalLink } from "lucide-react"
import { getPopularRestaurants, type Restaurant } from "@/services/api"

interface LocationSelectorProps {
  onLocationChange: (location: string) => void
}

export default function LocationSelector({ onLocationChange }: Readonly<LocationSelectorProps>) {
  const navigate = useNavigate()
  const [selectedLocation, setSelectedLocation] = useState("")
  const [customLocation, setCustomLocation] = useState("")
  const [popularRestaurants, setPopularRestaurants] = useState<Restaurant[]>([])
  const [popularCities, setPopularCities] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        setIsLoading(true)
        const fetchedRestaurants = await getPopularRestaurants()
        setPopularRestaurants(fetchedRestaurants)

        setPopularCities(["Philadelphia", "Ashland City", "Affton", "Nashville", "Tampa Bay", "Indianapolis", "Largo"])
        
        setError(null)
      } catch (err) {
        console.error("Failed to fetch initial data:", err)
        setError("Could not load restaurant data. Please try again later.")
      } finally {
        setIsLoading(false)
      }
    }

    fetchInitialData()
  }, [])

  const handleLocationSelect = (location: string) => {
    setSelectedLocation(location)
    onLocationChange(location)
  }

  const handleCustomLocationSubmit = () => {
    if (customLocation.trim()) {
      handleLocationSelect(customLocation.trim())
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin" />
        <span className="ml-2">Loading data...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 text-red-700 bg-red-100 border border-red-400 rounded-lg">
        <div className="flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2"/>
          <strong>Error:</strong>
        </div>
        <p>{error}</p>
      </div>
    )
  }

  return (
    <Tabs defaultValue="restaurant" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="restaurant" className="text-xs">
          Popular
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
              key={restaurant.id}
              variant="outline"
              className="justify-start h-auto p-3 text-left hover:bg-primary hover:text-primary-foreground"
              onClick={() => {
                localStorage.setItem(`restaurant_${restaurant.id}`, JSON.stringify(restaurant));
                navigate(`/restaurant/${restaurant.id}`);
              }}
            >
              <Building className="w-4 h-4 mr-2 flex-shrink-0" />
              <div className="flex flex-col flex-1">
                <span className="font-semibold">{restaurant.name}</span>
                <span className="text-xs text-muted-foreground">{restaurant.address}</span>
              </div>
              <ExternalLink className="w-4 h-4 ml-2 flex-shrink-0" />
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
            placeholder="e.g., Nashville, TN or 37203"
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
              className="cursor-pointer hover:bg-primary hover:text-primary-foreground text-sm p-2"
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