"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { MapPin, Search, Utensils, Star, Clock, Euro, Navigation } from "lucide-react"
import LocationSelector from "@/components/location-selector"
import CategorySelector from "@/components/category-selector"
import AttributeSelector from "@/components/attribute-selector"

import OpeningHoursSelector from "@/components/opening-hours-selector"
import RestaurantResults from "@/components/restaurant-results"

interface Preferences {
  price: number[]
  distance: number[]
  rating: number[]
  waitTime: number[]
}

interface SearchCriteria {
  location: string
  categories: string[]
  attributes: string[]
  preferences: Preferences
  requestedDay: string | null
  requestedTime: string | null
}

export default function RestaurantFinder() {
  const [activeTab, setActiveTab] = useState("criteria")
  const [searchCriteria, setSearchCriteria] = useState<SearchCriteria>({
    location: "",
    categories: [],
    attributes: [],
    preferences: {
      price: [50],
      distance: [50],
      rating: [50],
      waitTime: [50],
    },

    requestedDay: null,
    requestedTime: null,
  })

  const handleLocationChange = (location: string) => {
    setSearchCriteria((prev) => ({ ...prev, location }))
  }

  const handleCategoriesChange = (categories: string[]) => {
    setSearchCriteria((prev) => ({ ...prev, categories }))
  }

  const handleAttributeChange = (attributes: string[]) => {
    console.log('DEBUG: handleAttributeChange called with:', attributes)
    setSearchCriteria((prev) => ({ ...prev, attributes }))
  }

  const handlePreferenceChange = (key: keyof Preferences, value: number[]) => {
    setSearchCriteria((prev) => ({
      ...prev,
      preferences: { ...prev.preferences, [key]: value },
    }))
  }



  const handleOpeningHoursChange = (day: string | null, time: string | null) => {
    setSearchCriteria((prev) => ({ ...prev, requestedDay: day, requestedTime: time }))
  }

  const handleSearch = () => {
    setActiveTab("results")
  }

  const isSearchReady = searchCriteria.location

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Restaurant Finder</h1>
          <p className="text-lg text-gray-600">Find the perfect restaurant for any occasion</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="criteria" className="flex items-center gap-2">
              <Search className="w-4 h-4" />
              Search criteria
            </TabsTrigger>
            <TabsTrigger value="results" className="flex items-center gap-2">
              <Utensils className="w-4 h-4" />
              Results
            </TabsTrigger>
          </TabsList>

          <TabsContent value="criteria" className="space-y-6">
            <Card className="bg-gradient-to-r from-orange-50 to-red-50">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-3 text-xl">
                  <MapPin className="w-6 h-6 text-orange-500" />
                  Location (Required)
                </CardTitle>
                <CardDescription className="text-base">Choose a restaurant, enter a place, or name a city to get started</CardDescription>
              </CardHeader>
              <CardContent className="pt-2">
                <LocationSelector onLocationChange={handleLocationChange} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Optional filters</CardTitle>
                <CardDescription className="text-base">Refine your search with additional criteria</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <Label className="text-base font-medium mb-3 block">Categories</Label>
                  <CategorySelector onCategoriesChange={handleCategoriesChange} />
                </div>

                <Separator />

                <div>
                  <Label className="text-base font-medium mb-3 block">Attributes</Label>
                  <AttributeSelector onAttributeChange={handleAttributeChange} />
                </div>

                <Separator />

                <div>
                  <Label className="text-base font-medium mb-3 block">Opening Hours</Label>
                  <OpeningHoursSelector onOpeningHoursChange={handleOpeningHoursChange} />
                </div>

                <Separator />

                <div>
                  <Label className="text-base font-medium mb-4 block">Weight Preferences</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                          <Euro className="w-4 h-4" />
                          Price
                        </Label>
                        <span className="text-sm text-gray-500">{searchCriteria.preferences.price[0]}%</span>
                      </div>
                      <Slider
                        value={searchCriteria.preferences.price}
                        onValueChange={(value) => handlePreferenceChange("price", value)}
                        max={100}
                        step={25}
                        className="w-full"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                          <Navigation className="w-4 h-4" />
                          Distance
                        </Label>
                        <span className="text-sm text-gray-500">{searchCriteria.preferences.distance[0]}%</span>
                      </div>
                      <Slider
                        value={searchCriteria.preferences.distance}
                        onValueChange={(value) => handlePreferenceChange("distance", value)}
                        max={100}
                        step={25}
                        className="w-full"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                          <Star className="w-4 h-4" />
                          Rating
                        </Label>
                        <span className="text-sm text-gray-500">{searchCriteria.preferences.rating[0]}%</span>
                      </div>
                      <Slider
                        value={searchCriteria.preferences.rating}
                        onValueChange={(value) => handlePreferenceChange("rating", value)}
                        max={100}
                        step={25}
                        className="w-full"
                      />
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <Label className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
                          Category Similarity
                        </Label>
                        <span className="text-sm text-gray-500">{searchCriteria.preferences.waitTime[0]}%</span>
                      </div>
                      <Slider
                        value={searchCriteria.preferences.waitTime}
                        onValueChange={(value) => handlePreferenceChange("waitTime", value)}
                        max={100}
                        step={25}
                        className="w-full"
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {(searchCriteria.location ||
              searchCriteria.categories.length > 0 ||
              searchCriteria.attributes.length > 0 ||
              searchCriteria.requestedDay ||
              searchCriteria.requestedTime) && (
              <Card>
                <CardHeader>
                  <CardTitle>Current Selection</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {searchCriteria.location && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {searchCriteria.location}
                      </Badge>
                    )}
                    {searchCriteria.categories.map((category: string) => (
                      <Badge key={category} variant="outline">
                        {category}
                      </Badge>
                    ))}
                    {searchCriteria.attributes.map((attribute) => (
                      <Badge key={attribute} variant="outline">{attribute}</Badge>
                    ))}
                    {(searchCriteria.requestedDay || searchCriteria.requestedTime) && (
                      <Badge variant="outline" className="bg-blue-50 border-blue-200">
                        <Clock className="w-3 h-3 mr-1" />
                        {searchCriteria.requestedDay}
                        {searchCriteria.requestedDay && searchCriteria.requestedTime && " "}
                        {searchCriteria.requestedTime}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            <div className="flex justify-center">
              <Button onClick={handleSearch} disabled={!isSearchReady} size="lg" className="px-8">
                <Search className="w-4 h-4 mr-2" />
                Find Restaurants
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="results">
            <RestaurantResults searchCriteria={searchCriteria} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}